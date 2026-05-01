"""Validation job endpoints."""

from datetime import datetime
from typing import Optional
from uuid import UUID
import asyncio

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db, CurrentUser
from app.core.config import settings
from app.infrastructure.persistence.document_repository import DocumentRepository
from app.infrastructure.persistence.template_repository import TemplateRepository
from app.infrastructure.persistence.models import ValidationJobModel, ValidationResultModel
from app.domain.entities.validation_result import ValidationResult, Severity
from app.domain.services.rule_engine import RuleEngine
from app.domain.services.template_service import TemplateService
from app.domain.services.ai_enhancement_service import AIEnhancementService
from app.infrastructure.docx.document_parser import DocumentParser

router = APIRouter()


class ValidationCreateRequest(BaseModel):
    document_id: str
    template_id: str


class ValidationResultItem(BaseModel):
    id: str
    rule_id: str
    severity: str
    element_path: str
    expected_value: str
    actual_value: str
    message: str
    auto_fixable: bool
    ai_enhanced: bool
    confidence: Optional[float] = None


class ValidationSummary(BaseModel):
    total: int
    errors: int
    warnings: int
    infos: int
    auto_fixable: int


class ValidationJobResponse(BaseModel):
    job_id: str
    status: str
    created_at: str


class ValidationResponse(BaseModel):
    id: str
    document_id: str
    template_id: str
    status: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    results: list[ValidationResultItem] = []
    summary: Optional[ValidationSummary] = None


async def _run_validation_job(
    job_id: UUID,
    document_id: UUID,
    template_id: UUID,
    db_url: str,
):
    """Background task to run validation."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    engine = create_engine(db_url)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        job = db.query(ValidationJobModel).filter(ValidationJobModel.id == job_id).first()
        if not job:
            return

        job.status = "running"
        job.started_at = datetime.utcnow()
        db.commit()

        doc_repo = DocumentRepository(db)
        template_repo = TemplateRepository(db)

        document = doc_repo.find_by_id(document_id)
        template = template_repo.find_by_id(template_id)

        if not document or not template:
            job.status = "failed"
            job.error_message = "Document or template not found"
            job.completed_at = datetime.utcnow()
            db.commit()
            return

        from app.domain.entities.document import DocumentStatus
        document.status = DocumentStatus.PROCESSING.value
        doc_repo.update(document)

        parser = DocumentParser()
        parsed_doc = parser.parse(document.file_path)

        template_service = TemplateService(template_repo)
        ai_service = AIEnhancementService()
        ai_service.disable()

        rule_engine = RuleEngine(template_service, ai_service)

        from app.domain.services.template_service import TemplateService
        template_entity = template_service.get_template(template_id)
        if not template_entity:
            job.status = "failed"
            job.error_message = "Template not found"
            job.completed_at = datetime.utcnow()
            db.commit()
            return

        report = rule_engine.validate(document, parsed_doc, template_entity)

        for result in report.results:
            result_model = ValidationResultModel(
                id=result.id,
                job_id=job_id,
                rule_id=result.rule_id,
                rule_name=result.rule_name,
                element_path=result.element_path,
                severity=result.severity.value if isinstance(result.severity, Severity) else result.severity,
                expected_value=result.expected_value,
                actual_value=result.actual_value,
                message=result.message,
                auto_fixable=result.auto_fixable,
                ai_enhanced=result.ai_enhanced,
                confidence=result.confidence,
                created_at=result.created_at,
            )
            db.add(result_model)

        job.status = "completed"
        job.completed_at = datetime.utcnow()
        db.commit()

        document.status = DocumentStatus.COMPLETED.value
        doc_repo.update(document)

    except Exception as e:
        job = db.query(ValidationJobModel).filter(ValidationJobModel.id == job_id).first()
        if job:
            job.status = "failed"
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()
            db.commit()

        doc_repo = DocumentRepository(db)
        doc = doc_repo.find_by_id(document_id)
        if doc:
            from app.domain.entities.document import DocumentStatus
            doc.status = DocumentStatus.FAILED.value
            doc_repo.update(doc)
    finally:
        db.close()


@router.post("/", status_code=202)
async def create_validation(
    request: ValidationCreateRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks(),
):
    """Create a new validation job.

    Args:
        request: Contains document_id and template_id
        current_user: Authenticated user
        db: Database session
        background_tasks: FastAPI background tasks

    Returns:
        Job information with ID and status
    """
    doc_repo = DocumentRepository(db)
    template_repo = TemplateRepository(db)

    try:
        document_id = UUID(request.document_id)
        template_id = UUID(request.template_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid ID format")

    document = doc_repo.find_by_id(document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    if document.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    template = template_repo.find_by_id(template_id)
    if template is None:
        raise HTTPException(status_code=404, detail="Template not found")

    job = ValidationJobModel(
        document_id=document_id,
        template_id=template_id,
        status="pending",
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    background_tasks.add_task(
        _run_validation_job,
        job.id,
        document_id,
        template_id,
        str(settings.database_url),
    )

    return ValidationJobResponse(
        job_id=str(job.id),
        status=job.status,
        created_at=job.created_at.isoformat(),
    )


@router.get("/{job_id}", response_model=ValidationResponse)
async def get_validation(
    job_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get validation job status and results.

    Args:
        job_id: Validation job UUID
        current_user: Authenticated user
        db: Database session

    Returns:
        Validation job with results
    """
    try:
        job_uuid = UUID(job_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid job ID format")

    job = db.query(ValidationJobModel).filter(
        ValidationJobModel.id == job_uuid
    ).first()

    if job is None:
        raise HTTPException(status_code=404, detail="Validation job not found")

    document = db.query(
        db.query(ValidationJobModel).filter(ValidationJobModel.id == job_uuid).first().document_id
    )
    doc_repo = DocumentRepository(db)
    doc = doc_repo.find_by_id(job.document_id)
    if doc and doc.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    results = db.query(ValidationResultModel).filter(
        ValidationResultModel.job_id == job_uuid
    ).all()

    summary = None
    if results:
        summary = ValidationSummary(
            total=len(results),
            errors=sum(1 for r in results if r.severity == "error"),
            warnings=sum(1 for r in results if r.severity == "warning"),
            infos=sum(1 for r in results if r.severity == "info"),
            auto_fixable=sum(1 for r in results if r.auto_fixable),
        )

    return ValidationResponse(
        id=str(job.id),
        document_id=str(job.document_id),
        template_id=str(job.template_id),
        status=job.status,
        started_at=job.started_at.isoformat() if job.started_at else None,
        completed_at=job.completed_at.isoformat() if job.completed_at else None,
        results=[
            ValidationResultItem(
                id=str(r.id),
                rule_id=r.rule_id,
                severity=r.severity,
                element_path=r.element_path,
                expected_value=r.expected_value or "",
                actual_value=r.actual_value or "",
                message=r.message or "",
                auto_fixable=r.auto_fixable,
                ai_enhanced=r.ai_enhanced,
                confidence=r.confidence,
            )
            for r in results
        ],
        summary=summary,
    )