"""Specification-based validation endpoints."""

import tempfile
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_current_user, CurrentUser
from app.application.spec.spec_application_service import SpecApplicationService
from app.application.exceptions import NotFoundError, AccessDeniedError, ValidationError
from app.domain.services.correction_executor import CorrectionExecutor

router = APIRouter()


class SpecParseResponse(BaseModel):
    session_id: str
    rules_count: int
    extraction_summary: dict
    preview_rules: list


class SpecValidationResponse(BaseModel):
    session_id: str
    report_id: str
    document_name: Optional[str] = None
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
    created_at: str
    total_count: int
    error_count: int
    warning_count: int
    info_count: int
    violations: list[ViolationDetailResponse]


def _map_exception(e: Exception) -> HTTPException:
    """Map application exceptions to HTTP exceptions."""
    if isinstance(e, NotFoundError):
        return HTTPException(status_code=404, detail=e.message)
    if isinstance(e, AccessDeniedError):
        return HTTPException(status_code=403, detail=e.message)
    if isinstance(e, ValidationError):
        return HTTPException(status_code=422, detail=e.message)
    return HTTPException(status_code=500, detail=str(e))


@router.post("/parse-spec", response_model=SpecParseResponse)
async def parse_specification(
    file: UploadFile = File(...),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Parse a specification document and extract rules."""
    if not file.filename or not file.filename.endswith(".docx"):
        raise HTTPException(status_code=422, detail="Only .docx files are supported")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp_file:
        content = await file.read()
        tmp_file.write(content)
        tmp_path = Path(tmp_file.name)

    try:
        service = SpecApplicationService(db)
        result = service.parse_spec(tmp_path, current_user.id)
        return SpecParseResponse(
            session_id=result["session_id"],
            rules_count=result["rules_count"],
            extraction_summary=result["extraction_summary"],
            preview_rules=result["preview_rules"],
        )
    except Exception as e:
        raise _map_exception(e)
    finally:
        if tmp_path.exists():
            tmp_path.unlink()


@router.get("/spec-sessions/{session_id}")
async def get_spec_session(
    session_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a spec session by ID."""
    try:
        service = SpecApplicationService(db)
        result = service.get_spec_session(session_id, current_user.id)
        return result
    except Exception as e:
        raise _map_exception(e)


@router.post("/validate-with-spec", response_model=SpecValidationResponse)
async def validate_with_specification(
    document_file: UploadFile = File(...),
    session_id: str = Query(...),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Validate a thesis document against spec rules."""
    if not document_file.filename or not document_file.filename.endswith(".docx"):
        raise HTTPException(status_code=422, detail="Only .docx files are supported")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp_file:
        content = await document_file.read()
        tmp_file.write(content)
        tmp_path = Path(tmp_file.name)

    try:
        service = SpecApplicationService(db)
        result = service.validate_with_spec(
            tmp_path, session_id, document_file.filename, current_user.id
        )
        return SpecValidationResponse(
            session_id=result["session_id"],
            report_id=result["report_id"],
            document_name=result["document_name"],
            results_count=result["results_count"],
            error_count=result["error_count"],
            warning_count=result["warning_count"],
            info_count=result["info_count"],
        )
    except Exception as e:
        raise _map_exception(e)
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
    try:
        service = SpecApplicationService(db)
        result = service.get_validation_report(report_id, current_user.id)
        return ValidationReportResponse(
            report_id=result["report_id"],
            session_id=result["session_id"],
            document_name=result["document_name"],
            template_name=result["template_name"],
            created_at=result["created_at"].isoformat() if hasattr(result["created_at"], "isoformat") else str(result["created_at"]),
            total_count=result["total_count"],
            error_count=result["error_count"],
            warning_count=result["warning_count"],
            info_count=result["info_count"],
            violations=[
                ViolationDetailResponse(
                    id=v["id"],
                    category=v["category"],
                    severity=v["severity"],
                    description=v["description"],
                    paragraph_index=v.get("paragraph_index"),
                    text=v.get("text"),
                    original_content=v.get("original_content", ""),
                    suggested_fix=v.get("suggested_fix", ""),
                    context_before=v.get("context_before"),
                    context_after=v.get("context_after"),
                    user_modified_fix=v.get("user_modified_fix"),
                )
                for v in result["violations"]
            ],
        )
    except Exception as e:
        raise _map_exception(e)


@router.delete("/spec-sessions/{session_id}", status_code=204)
async def delete_spec_session(
    session_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a spec session."""
    try:
        service = SpecApplicationService(db)
        service.delete_spec_session(session_id, current_user.id)
    except Exception as e:
        raise _map_exception(e)