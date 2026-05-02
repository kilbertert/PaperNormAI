"""Specification-based validation endpoints.

Provides API endpoints for:
1. Upload and parse specification document -> extract rules
2. Validate user document against extracted rules
"""

from pathlib import Path
from typing import Optional
import tempfile
import hashlib
import shutil

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_current_user, CurrentUser
from app.core.config import settings
from app.infrastructure.docx.specification_to_rules import SpecificationToRulesPipeline
from app.infrastructure.docx.document_parser import DocumentParser
from app.domain.services.rule_engine import RuleEngine
from app.domain.services.template_service import TemplateService
from app.domain.services.ai_enhancement_service import AIEnhancementService
from app.infrastructure.persistence.template_repository import TemplateRepository

router = APIRouter()


class SpecParseResponse(BaseModel):
    """Response when specification rules have been extracted."""
    session_id: str
    rules_count: int
    extraction_summary: dict
    preview_rules: list


class SpecValidationRequest(BaseModel):
    """Request to validate a document against extracted rules."""
    session_id: str


class SpecValidationResponse(BaseModel):
    """Response with validation results."""
    session_id: str
    results_count: int
    error_count: int
    warning_count: int
    info_count: int


# In-memory storage for extracted rules (for MVP)
# In production, this would be stored in database or Redis
_spec_sessions = {}


def _calculate_file_hash(file_path: Path) -> str:
    """Calculate SHA256 hash of a file."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


@router.post("/parse-spec", response_model=SpecParseResponse)
async def parse_specification(
    file: UploadFile = File(...),
    current_user: CurrentUser = Depends(get_current_user),
):
    """Parse a specification document and extract validation rules.

    This endpoint:
    1. Receives a .docx file containing formatting specifications
    2. Parses it to extract rules using pattern matching + AI
    3. Returns the extracted rules for preview

    The session_id can then be used to validate user documents.
    """
    if not file.filename or not file.filename.endswith(".docx"):
        raise HTTPException(
            status_code=422,
            detail="Only .docx files are supported",
        )

    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp_file:
        content = await file.read()
        tmp_file.write(content)
        tmp_path = Path(tmp_file.name)

    try:
        pipeline = SpecificationToRulesPipeline()
        result = pipeline.process(tmp_path)

        session_id = _calculate_file_hash(tmp_path)[:16]

        _spec_sessions[session_id] = {
            "user_id": str(current_user.id),
            "rules": result.rules,
            "spec_file": str(tmp_path),
            "summary": result.extraction_summary,
        }

        preview_rules = [
            {
                "id": r.id,
                "name": r.name,
                "level": r.level.value if hasattr(r.level, 'value') else str(r.level),
                "description": r.description[:100],
                "params": r.params,
            }
            for r in result.rules[:10]
        ]

        return SpecParseResponse(
            session_id=session_id,
            rules_count=len(result.rules),
            extraction_summary=result.extraction_summary,
            preview_rules=preview_rules,
        )

    finally:
        if tmp_path.exists():
            tmp_path.unlink()


@router.get("/spec-sessions/{session_id}")
async def get_spec_session(
    session_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Get details of a parsed specification session."""
    session = _spec_sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session["user_id"] != str(current_user.id):
        raise HTTPException(status_code=403, detail="Access denied")

    return {
        "session_id": session_id,
        "rules_count": len(session["rules"]),
        "summary": session["summary"],
    }


@router.post("/validate-with-spec", response_model=SpecValidationResponse)
async def validate_with_specification(
    document_file: UploadFile = File(...),
    session_id: str = Query(...),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Validate a document against rules extracted from a specification.

    Workflow:
    1. User has previously uploaded a specification document
    2. User now uploads their thesis/paper .docx
    3. System validates against the extracted rules
    4. Returns validation report
    """
    session = _spec_sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Specification session not found")

    if session["user_id"] != str(current_user.id):
        raise HTTPException(status_code=403, detail="Access denied")

    if not document_file.filename or not document_file.filename.endswith(".docx"):
        raise HTTPException(
            status_code=422,
            detail="Only .docx files are supported",
        )

    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp_file:
        content = await document_file.read()
        tmp_file.write(content)
        tmp_path = Path(tmp_file.name)

    try:
        parser = DocumentParser()
        parsed_doc = parser.parse(tmp_path)

        from app.domain.entities.document import Document, DocumentStatus
        from app.domain.entities.template import Template, DegreeType
        from uuid import UUID, uuid4

        document = Document(
            id=uuid4(),
            user_id=current_user.id,
            original_filename=document_file.filename,
            file_path=tmp_path,
            file_hash=_calculate_file_hash(tmp_path),
            status=DocumentStatus.PROCESSING,
        )

        template = Template(
            id=uuid4(),
            university="Specification-based",
            degree_type=DegreeType.BACHELOR,
            discipline="Custom",
            version="1.0",
            rules=[r.params for r in session["rules"]],
        )

        ai_enhancement = AIEnhancementService()
        template_service = TemplateService()
        rule_engine = RuleEngine(template_service, ai_enhancement)

        report = rule_engine.validate(document, parsed_doc, template)

        error_count = sum(1 for r in report.results if r.severity.value == "error")
        warning_count = sum(1 for r in report.results if r.severity.value == "warning")
        info_count = sum(1 for r in report.results if r.severity.value == "info")

        return SpecValidationResponse(
            session_id=session_id,
            results_count=len(report.results),
            error_count=error_count,
            warning_count=warning_count,
            info_count=info_count,
        )

    finally:
        if tmp_path.exists():
            tmp_path.unlink()


@router.delete("/spec-sessions/{session_id}", status_code=204)
async def delete_spec_session(
    session_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Delete a specification session and free memory."""
    session = _spec_sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session["user_id"] != str(current_user.id):
        raise HTTPException(status_code=403, detail="Access denied")

    del _spec_sessions[session_id]
