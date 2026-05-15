"""Correction job endpoints."""

from datetime import datetime
from pathlib import Path
from typing import Optional
from uuid import UUID
import json
import asyncio

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db, CurrentUser
from app.core.config import settings
from app.infrastructure.persistence.document_repository import DocumentRepository
from app.infrastructure.persistence.template_repository import TemplateRepository
from app.infrastructure.persistence.models import CorrectionJobModel, CorrectionPlanModel, ValidationResultModel
from app.domain.entities.correction_plan import CorrectionPlan, CorrectionStatus, CorrectionActionType
from app.domain.services.correction_executor import CorrectionExecutor
from app.infrastructure.docx.document_parser import DocumentParser
from app.infrastructure.docx.document_writer import DocumentWriter

router = APIRouter()


class CorrectionCreateRequest(BaseModel):
    document_id: str
    plan_ids: list[str]


class CorrectionJobResponse(BaseModel):
    job_id: str
    status: str
    created_at: str


class CorrectionPlanResponse(BaseModel):
    id: str
    rule_id: str
    action_type: str
    target_path: str
    original_value: str
    planned_value: str
    status: str


class CorrectionResponse(BaseModel):
    id: str
    document_id: str
    status: str
    output_path: Optional[str] = None
    error_message: Optional[str] = None
    plans: list[CorrectionPlanResponse] = []
    created_at: str
    completed_at: Optional[str] = None


async def _run_correction_job(
    job_id: UUID,
    document_id: UUID,
    plan_ids: list[str],
    db_url: str,
):
    """Background task to run correction."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    engine = create_engine(db_url)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        job = db.query(CorrectionJobModel).filter(CorrectionJobModel.id == job_id).first()
        if not job:
            return

        job.status = "running"
        job.started_at = datetime.utcnow()
        db.commit()

        doc_repo = DocumentRepository(db)
        document = doc_repo.find_by_id(document_id)

        if not document:
            job.status = "failed"
            job.error_message = "Document not found"
            job.completed_at = datetime.utcnow()
            db.commit()
            return

        plans = []
        for plan_id_str in plan_ids:
            try:
                plan_uuid = UUID(plan_id_str)
                plan_model = db.query(CorrectionPlanModel).filter(
                    CorrectionPlanModel.id == plan_uuid
                ).first()
                if plan_model:
                    plans.append(CorrectionPlan(
                        id=plan_model.id,
                        result_id=plan_model.result_id,
                        action_type=CorrectionActionType(plan_model.action_type),
                        target_path=plan_model.target_path,
                        original_value=plan_model.original_value,
                        planned_value=plan_model.planned_value,
                        status=CorrectionStatus(plan_model.status),
                    ))
            except (ValueError, TypeError):
                continue

        for plan in plans:
            plan.approve()

        parser = DocumentParser()
        parsed_doc = parser.parse(document.file_path)

        executor = CorrectionExecutor()
        modified_doc = executor.execute(document, parsed_doc, plans)

        output_filename = f"{document_id}_corrected.docx"
        output_path = settings.upload_dir / output_filename
        output_path.parent.mkdir(parents=True, exist_ok=True)

        writer = DocumentWriter()
        writer.write_to_docx(modified_doc, output_path)

        job.output_path = str(output_path)
        job.status = "completed"
        job.completed_at = datetime.utcnow()
        db.commit()

    except Exception as e:
        job = db.query(CorrectionJobModel).filter(CorrectionJobModel.id == job_id).first()
        if job:
            job.status = "failed"
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()
            db.commit()
    finally:
        db.close()


@router.post("/", status_code=202)
async def create_correction(
    request: CorrectionCreateRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks(),
):
    """Create a new correction job.

    Args:
        request: Contains document_id and plan_ids
        current_user: Authenticated user
        db: Database session
        background_tasks: FastAPI background tasks

    Returns:
        Job information with ID and status
    """
    doc_repo = DocumentRepository(db)

    try:
        document_id = UUID(request.document_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid document ID format")

    document = doc_repo.find_by_id(document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    if document.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    job = CorrectionJobModel(
        document_id=document_id,
        plan_ids_json=json.dumps(request.plan_ids),
        status="pending",
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    background_tasks.add_task(
        _run_correction_job,
        job.id,
        document_id,
        request.plan_ids,
        str(settings.database_url),
    )

    return CorrectionJobResponse(
        job_id=str(job.id),
        status=job.status,
        created_at=job.created_at.isoformat(),
    )


@router.get("/{job_id}", response_model=CorrectionResponse)
async def get_correction(
    job_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get correction job status.

    Args:
        job_id: Correction job UUID
        current_user: Authenticated user
        db: Database session

    Returns:
        Correction job with status
    """
    try:
        job_uuid = UUID(job_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid job ID format")

    job = db.query(CorrectionJobModel).filter(
        CorrectionJobModel.id == job_uuid
    ).first()

    if job is None:
        raise HTTPException(status_code=404, detail="Correction job not found")

    doc_repo = DocumentRepository(db)
    doc = doc_repo.find_by_id(job.document_id)
    if doc and doc.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    plan_ids = json.loads(job.plan_ids_json) if job.plan_ids_json else []
    plans = []
    for plan_id_str in plan_ids:
        try:
            plan_uuid = UUID(plan_id_str)
            plan_model = db.query(CorrectionPlanModel).filter(
                CorrectionPlanModel.id == plan_uuid
            ).first()
            if plan_model:
                plans.append(CorrectionPlanResponse(
                    id=str(plan_model.id),
                    rule_id=plan_model.result_id,
                    action_type=plan_model.action_type,
                    target_path=plan_model.target_path,
                    original_value=plan_model.original_value or "",
                    planned_value=plan_model.planned_value or "",
                    status=plan_model.status,
                ))
        except (ValueError, TypeError):
            continue

    return CorrectionResponse(
        id=str(job.id),
        document_id=str(job.document_id),
        status=job.status,
        output_path=job.output_path,
        error_message=job.error_message,
        plans=plans,
        created_at=job.created_at.isoformat(),
        completed_at=job.completed_at.isoformat() if job.completed_at else None,
    )


@router.get("/{job_id}/download")
async def download_corrected_document(
    job_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Download the corrected document.

    Args:
        job_id: Correction job UUID
        current_user: Authenticated user
        db: Database session

    Returns:
        FileResponse with the corrected .docx file
    """
    try:
        job_uuid = UUID(job_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid job ID format")

    job = db.query(CorrectionJobModel).filter(
        CorrectionJobModel.id == job_uuid
    ).first()

    if job is None:
        raise HTTPException(status_code=404, detail="Correction job not found")

    if job.status != "completed" or not job.output_path:
        raise HTTPException(
            status_code=400,
            detail="Correction job not completed or no output file",
        )

    doc_repo = DocumentRepository(db)
    doc = doc_repo.find_by_id(job.document_id)
    if doc and doc.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    file_path = Path(job.output_path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found on storage")

    return FileResponse(
        path=file_path,
        filename=f"corrected_{doc.original_filename if doc else 'document.docx'}",
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )