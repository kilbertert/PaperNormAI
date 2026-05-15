"""Correction job endpoints."""

from pathlib import Path
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db, CurrentUser
from app.application.correction.correction_application_service import CorrectionApplicationService
from app.application.exceptions import NotFoundError, AccessDeniedError, ValidationError

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
        from app.infrastructure.persistence.models import CorrectionJobModel, CorrectionPlanModel
        from app.domain.entities.correction_plan import CorrectionPlan, CorrectionStatus, CorrectionActionType
        from app.infrastructure.docx.document_parser import DocumentParser
        from app.infrastructure.docx.document_writer import DocumentWriter
        from app.domain.services.correction_executor import CorrectionExecutor
        from app.infrastructure.persistence.document_repository import DocumentRepository
        from app.core.config import settings

        job = db.query(CorrectionJobModel).filter(CorrectionJobModel.id == job_id).first()
        if not job:
            return

        job.status = "running"
        job.started_at = __import__("datetime").datetime.utcnow()
        db.commit()

        doc_repo = DocumentRepository(db)
        document = doc_repo.find_by_id(document_id)

        if not document:
            job.status = "failed"
            job.error_message = "Document not found"
            job.completed_at = __import__("datetime").datetime.utcnow()
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
        job.completed_at = __import__("datetime").datetime.utcnow()
        db.commit()

    except Exception as e:
        job = db.query(CorrectionJobModel).filter(CorrectionJobModel.id == job_id).first()
        if job:
            job.status = "failed"
            job.error_message = str(e)
            job.completed_at = __import__("datetime").datetime.utcnow()
            db.commit()
    finally:
        db.close()


def _map_exception(e: Exception) -> HTTPException:
    """Map application exceptions to HTTP exceptions."""
    if isinstance(e, NotFoundError):
        return HTTPException(status_code=404, detail=e.message)
    if isinstance(e, AccessDeniedError):
        return HTTPException(status_code=403, detail=e.message)
    if isinstance(e, ValidationError):
        return HTTPException(status_code=422, detail=e.message)
    return HTTPException(status_code=500, detail=str(e))


@router.post("/", status_code=202)
async def create_correction(
    request: CorrectionCreateRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks(),
):
    """Create a new correction job."""
    try:
        document_id = UUID(request.document_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid document ID format")

    def background_fn(job_id, doc_id, plan_ids, db_url):
        background_tasks.add_task(_run_correction_job, job_id, doc_id, plan_ids, db_url)

    service = CorrectionApplicationService(db)
    try:
        result = service.create_correction_job(
            document_id,
            request.plan_ids,
            current_user.id,
            background_fn,
        )
        return CorrectionJobResponse(
            job_id=result["job_id"],
            status=result["status"],
            created_at=result["created_at"],
        )
    except Exception as e:
        raise _map_exception(e)


@router.get("/{job_id}", response_model=CorrectionResponse)
async def get_correction(
    job_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get correction job status."""
    try:
        job_uuid = UUID(job_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid job ID format")

    service = CorrectionApplicationService(db)
    try:
        result = service.get_correction_job(job_uuid, current_user.id)
        return CorrectionResponse(
            id=result["id"],
            document_id=result["document_id"],
            status=result["status"],
            output_path=result.get("output_path"),
            error_message=result.get("error_message"),
            plans=[
                CorrectionPlanResponse(
                    id=p["id"],
                    rule_id=p["rule_id"],
                    action_type=p["action_type"],
                    target_path=p["target_path"],
                    original_value=p["original_value"],
                    planned_value=p["planned_value"],
                    status=p["status"],
                )
                for p in result["plans"]
            ],
            created_at=result["created_at"],
            completed_at=result.get("completed_at"),
        )
    except Exception as e:
        raise _map_exception(e)


@router.get("/{job_id}/download")
async def download_corrected_document(
    job_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Download the corrected document."""
    try:
        job_uuid = UUID(job_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid job ID format")

    service = CorrectionApplicationService(db)
    try:
        result = service.get_download_info(job_uuid, current_user.id)
        return FileResponse(
            path=result["file_path"],
            filename=result["filename"],
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
    except Exception as e:
        raise _map_exception(e)