"""Specification-based validation endpoints."""

from pathlib import Path
import tempfile
import hashlib

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session, joinedload

from app.api.dependencies import get_db, get_current_user, CurrentUser
from app.infrastructure.docling.parser import DoclingDocumentParser
from app.infrastructure.ai.openai_provider import OpenAIProvider
from app.domain.services.rule_extraction_service import RuleExtractionService
from app.domain.services.semantic_validation_service import SemanticValidationService
from app.infrastructure.persistence.spec_session_repository import SpecSessionRepository
from app.infrastructure.persistence.models import ValidationReportModel, ViolationDetailModel

router = APIRouter()

# Application-level wiring: infrastructure implementations
_parser = DoclingDocumentParser()
_ai_provider = OpenAIProvider()


class SpecParseResponse(BaseModel):
    session_id: str
    rules_count: int
    extraction_summary: dict
    preview_rules: list


class SpecValidationResponse(BaseModel):
    session_id: str
    report_id: str
    results_count: int
    error_count: int
    warning_count: int
    info_count: int


class ViolationDetailResponse(BaseModel):
    id: str
    category: str
    severity: str
    description: str
    paragraph_index: Optional[int] = None
    text: Optional[str] = None
    original_content: str
    suggested_fix: str
    context_before: Optional[str] = None
    context_after: Optional[str] = None
    user_modified_fix: Optional[str] = None


class ValidationReportResponse(BaseModel):
    report_id: str
    session_id: str
    document_name: Optional[str] = None
    template_name: Optional[str] = None
    created_at: datetime
    total_count: int
    error_count: int
    warning_count: int
    info_count: int
    violations: List[ViolationDetailResponse] = []


def _calculate_file_hash(file_path: Path) -> str:
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


@router.post("/parse-spec", response_model=SpecParseResponse)
async def parse_specification(
    file: UploadFile = File(...),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not file.filename or not file.filename.endswith(".docx"):
        raise HTTPException(status_code=422, detail="Only .docx files are supported")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp_file:
        content = await file.read()
        tmp_file.write(content)
        tmp_path = Path(tmp_file.name)

    try:
        spec_doc = _parser.parse(tmp_path)
        rules_dicts = RuleExtractionService(document_parser=spec_doc, ai_provider=_ai_provider).extract_rules(spec_doc)
        session_id = _calculate_file_hash(tmp_path)[:16]
        summary = {"total_rules": len(rules_dicts), "extraction_method": "ai"}

        SpecSessionRepository(db).save(
            session_id=session_id,
            user_id=str(current_user.id),
            rules_dicts=rules_dicts,
            summary=summary,
        )

        return SpecParseResponse(
            session_id=session_id,
            rules_count=len(rules_dicts),
            extraction_summary=summary,
            preview_rules=rules_dicts[:10],
        )
    finally:
        if tmp_path.exists():
            tmp_path.unlink()


@router.get("/spec-sessions/{session_id}")
async def get_spec_session(
    session_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = SpecSessionRepository(db).find(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session["user_id"] != str(current_user.id):
        raise HTTPException(status_code=403, detail="Access denied")
    return {
        "session_id": session_id,
        "rules_count": len(session["rules_dicts"]),
        "summary": session["summary"],
    }


@router.post("/validate-with-spec", response_model=SpecValidationResponse)
async def validate_with_specification(
    document_file: UploadFile = File(...),
    session_id: str = Query(...),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = SpecSessionRepository(db).find(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Specification session not found")
    if session["user_id"] != str(current_user.id):
        raise HTTPException(status_code=403, detail="Access denied")
    if not document_file.filename or not document_file.filename.endswith(".docx"):
        raise HTTPException(status_code=422, detail="Only .docx files are supported")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp_file:
        content = await document_file.read()
        tmp_file.write(content)
        tmp_path = Path(tmp_file.name)

    try:
        thesis_doc = _parser.parse(tmp_path)
        report = SemanticValidationService(document_parser=thesis_doc, ai_provider=_ai_provider).validate(
            thesis_doc=thesis_doc,
            rules=session.get("rules_dicts", []),
            document_name=document_file.filename,
            template_name="spec-based",
        )

        # Step 7: Persist ValidationReport + ViolationDetails
        # Use domain object's existing ID (UUID), not truncated string
        report_id = str(report.id)

        report_model = ValidationReportModel(
            report_id=report_id,
            session_id=session_id,
            document_name=document_file.filename,
            template_name="spec-based",
            total_count=len(report.violations),
            error_count=sum(1 for v in report.violations if v.severity.value == "error"),
            warning_count=sum(1 for v in report.violations if v.severity.value == "warning"),
            info_count=sum(1 for v in report.violations if v.severity.value == "info"),
        )
        db.add(report_model)

        for v in report.violations:
            violation_id = str(v.id)  # Use domain object's existing UUID
            violation_model = ViolationDetailModel(
                id=violation_id,
                report_id=report_id,
                category=v.category.value if hasattr(v.category, 'value') else str(v.category),
                severity=v.severity.value if hasattr(v.severity, 'value') else str(v.severity),
                description=v.description,
                paragraph_index=v.location.paragraph_index if v.location else None,
                text=v.location.text if v.location else None,
                original_content=v.original_content,
                suggested_fix=v.suggested_fix,
                context_before=v.context_before,
                context_after=v.context_after,
                user_modified_fix=v.user_modified_fix,
            )
            db.add(violation_model)

        db.commit()

        return SpecValidationResponse(
            session_id=session_id,
            report_id=report_id,
            results_count=len(report.violations),
            error_count=sum(1 for v in report.violations if v.severity.value == "error"),
            warning_count=sum(1 for v in report.violations if v.severity.value == "warning"),
            info_count=sum(1 for v in report.violations if v.severity.value == "info"),
        )
    finally:
        if tmp_path.exists():
            tmp_path.unlink()


@router.get("/reports/{report_id}", response_model=ValidationReportResponse)
async def get_validation_report(
    report_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get validation report with all violation details."""
    report_model = db.query(ValidationReportModel).options(
        joinedload(ValidationReportModel.violations)
    ).filter(ValidationReportModel.report_id == report_id).first()

    if not report_model:
        raise HTTPException(status_code=404, detail="Report not found")

    # Verify user owns this report via the spec session
    session = SpecSessionRepository(db).find(report_model.session_id)
    if not session or session["user_id"] != str(current_user.id):
        raise HTTPException(status_code=403, detail="Access denied")

    return ValidationReportResponse(
        report_id=report_model.report_id,
        session_id=report_model.session_id,
        document_name=report_model.document_name,
        template_name=report_model.template_name,
        created_at=report_model.created_at,
        total_count=report_model.total_count,
        error_count=report_model.error_count,
        warning_count=report_model.warning_count,
        info_count=report_model.info_count,
        violations=[
            ViolationDetailResponse(
                id=v.id,
                category=v.category,
                severity=v.severity,
                description=v.description,
                paragraph_index=v.paragraph_index,
                text=v.text,
                original_content=v.original_content or "",
                suggested_fix=v.suggested_fix or "",
                context_before=v.context_before,
                context_after=v.context_after,
                user_modified_fix=v.user_modified_fix,
            )
            for v in report_model.violations
        ],
    )


@router.delete("/spec-sessions/{session_id}", status_code=204)
async def delete_spec_session(
    session_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = SpecSessionRepository(db)
    session = repo.find(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session["user_id"] != str(current_user.id):
        raise HTTPException(status_code=403, detail="Access denied")
    repo.delete(session_id)
