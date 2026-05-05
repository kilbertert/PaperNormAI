"""Specification-based validation endpoints.

Provides API endpoints for:
1. Upload and parse specification document -> extract rules
2. Validate user document against extracted rules
"""

from pathlib import Path
import tempfile
import hashlib

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_current_user, CurrentUser
from app.core.config import settings
from app.infrastructure.docling.parser import DoclingDocumentParser
from app.domain.services.rule_extraction_service import RuleExtractionService
from app.domain.services.semantic_validation_service import SemanticValidationService

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
        # Use DoclingDocumentParser for AI-based rule extraction
        docling_parser = DoclingDocumentParser()
        spec_doc = docling_parser.parse(tmp_path)

        # Use AI-based rule extraction service
        rule_extraction_service = RuleExtractionService()
        rules_dicts = rule_extraction_service.extract_rules(spec_doc)

        session_id = _calculate_file_hash(tmp_path)[:16]

        _spec_sessions[session_id] = {
            "user_id": str(current_user.id),
            "rules_dicts": rules_dicts,  # AI-extracted rule dicts
            "spec_file": str(tmp_path),
            "summary": {
                "total_rules": len(rules_dicts),
                "extraction_method": "ai",
            },
        }

        preview_rules = rules_dicts[:10]

        return SpecParseResponse(
            session_id=session_id,
            rules_count=len(rules_dicts),
            extraction_summary={
                "total_rules": len(rules_dicts),
                "extraction_method": "ai",
            },
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
        # Use DoclingDocumentParser for AI-based validation
        docling_parser = DoclingDocumentParser()
        thesis_doc = docling_parser.parse(tmp_path)

        # Get AI-extracted rules from session (already in dict format)
        rules_dicts = session.get("rules_dicts", [])

        semantic_validator = SemanticValidationService()
        report = semantic_validator.validate(
            thesis_doc=thesis_doc,
            rules=rules_dicts,
            document_name=document_file.filename,
            template_name="spec-based",
        )

        error_count = sum(1 for v in report.violations if v.severity.value == "error")
        warning_count = sum(1 for v in report.violations if v.severity.value == "warning")
        info_count = sum(1 for v in report.violations if v.severity.value == "info")

        return SpecValidationResponse(
            session_id=session_id,
            results_count=len(report.violations),
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
