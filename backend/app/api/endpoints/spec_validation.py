"""Specification-based validation endpoints."""

from pathlib import Path
import tempfile
import hashlib

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_current_user, CurrentUser
from app.infrastructure.docling.parser import DoclingDocumentParser
from app.domain.services.rule_extraction_service import RuleExtractionService
from app.domain.services.semantic_validation_service import SemanticValidationService
from app.infrastructure.persistence.spec_session_repository import SpecSessionRepository

router = APIRouter()


class SpecParseResponse(BaseModel):
    session_id: str
    rules_count: int
    extraction_summary: dict
    preview_rules: list


class SpecValidationResponse(BaseModel):
    session_id: str
    results_count: int
    error_count: int
    warning_count: int
    info_count: int


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
        spec_doc = DoclingDocumentParser().parse(tmp_path)
        rules_dicts = RuleExtractionService().extract_rules(spec_doc)
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
        thesis_doc = DoclingDocumentParser().parse(tmp_path)
        report = SemanticValidationService().validate(
            thesis_doc=thesis_doc,
            rules=session.get("rules_dicts", []),
            document_name=document_file.filename,
            template_name="spec-based",
        )
        return SpecValidationResponse(
            session_id=session_id,
            results_count=len(report.violations),
            error_count=sum(1 for v in report.violations if v.severity.value == "error"),
            warning_count=sum(1 for v in report.violations if v.severity.value == "warning"),
            info_count=sum(1 for v in report.violations if v.severity.value == "info"),
        )
    finally:
        if tmp_path.exists():
            tmp_path.unlink()


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
