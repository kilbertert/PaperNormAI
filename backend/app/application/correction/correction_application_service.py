"""Correction application service — orchestrates correction job creation and status."""

import json
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.application.exceptions import NotFoundError, AccessDeniedError, ValidationError
from app.infrastructure.persistence.document_repository import DocumentRepository
from app.infrastructure.persistence.models import CorrectionJobModel, CorrectionPlanModel
from app.domain.entities.correction_plan import CorrectionPlan, CorrectionStatus, CorrectionActionType
from app.core.config import settings


class CorrectionApplicationService:
    """Orchestrates correction job workflows."""

    def __init__(self, db: Session):
        self._db = db

    def create_correction_job(
        self,
        document_id: UUID,
        plan_ids: list[str],
        user_id: UUID,
        background_task_fn,
    ) -> dict:
        """Create a new correction job.

        Args:
            document_id: UUID of the document to correct
            plan_ids: List of correction plan IDs
            user_id: UUID of the current user
            background_task_fn: Function to enqueue background task

        Returns:
            dict with job_id, status, created_at

        Raises:
            NotFoundError: if document not found
            AccessDeniedError: if user doesn't own the document
            ValidationError: if document_id format is invalid
        """
        doc_repo = DocumentRepository(self._db)
        document = doc_repo.find_by_id(document_id)
        if document is None:
            raise NotFoundError("Document", str(document_id))
        if document.user_id != user_id:
            raise AccessDeniedError("Document", str(document_id))

        job = CorrectionJobModel(
            document_id=document_id,
            plan_ids_json=json.dumps(plan_ids),
            status="pending",
        )
        self._db.add(job)
        self._db.commit()
        self._db.refresh(job)

        background_task_fn(job.id, document_id, plan_ids, str(settings.database_url))

        return {
            "job_id": str(job.id),
            "status": job.status,
            "created_at": job.created_at.isoformat(),
        }

    def get_correction_job(self, job_id: UUID, user_id: UUID) -> dict:
        """Get correction job status with plans.

        Args:
            job_id: UUID of the correction job
            user_id: UUID of the current user

        Returns:
            dict with job details including plans

        Raises:
            NotFoundError: if job not found
            AccessDeniedError: if user doesn't own the document
            ValidationError: if job_id format is invalid
        """
        job = self._db.query(CorrectionJobModel).filter(
            CorrectionJobModel.id == job_id
        ).first()
        if job is None:
            raise NotFoundError("CorrectionJob", str(job_id))

        doc_repo = DocumentRepository(self._db)
        doc = doc_repo.find_by_id(job.document_id)
        if doc and doc.user_id != user_id:
            raise AccessDeniedError("CorrectionJob", str(job_id))

        plan_ids = json.loads(job.plan_ids_json) if job.plan_ids_json else []
        plans = []
        for plan_id_str in plan_ids:
            try:
                plan_uuid = UUID(plan_id_str)
                plan_model = self._db.query(CorrectionPlanModel).filter(
                    CorrectionPlanModel.id == plan_uuid
                ).first()
                if plan_model:
                    plans.append({
                        "id": str(plan_model.id),
                        "rule_id": plan_model.result_id,
                        "action_type": plan_model.action_type,
                        "target_path": plan_model.target_path,
                        "original_value": plan_model.original_value or "",
                        "planned_value": plan_model.planned_value or "",
                        "status": plan_model.status,
                    })
            except (ValueError, TypeError):
                continue

        return {
            "id": str(job.id),
            "document_id": str(job.document_id),
            "status": job.status,
            "output_path": job.output_path,
            "error_message": job.error_message,
            "plans": plans,
            "created_at": job.created_at.isoformat(),
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
        }

    def get_download_info(self, job_id: UUID, user_id: UUID) -> dict:
        """Get correction job download metadata.

        Args:
            job_id: UUID of the correction job
            user_id: UUID of the current user

        Returns:
            dict with file_path, filename, is_ready

        Raises:
            NotFoundError: if job not found
            AccessDeniedError: if user doesn't own the document
            ValidationError: if job not completed or no output file
        """
        job = self._db.query(CorrectionJobModel).filter(
            CorrectionJobModel.id == job_id
        ).first()
        if job is None:
            raise NotFoundError("CorrectionJob", str(job_id))

        doc_repo = DocumentRepository(self._db)
        doc = doc_repo.find_by_id(job.document_id)
        if doc and doc.user_id != user_id:
            raise AccessDeniedError("CorrectionJob", str(job_id))

        if job.status != "completed" or not job.output_path:
            raise ValidationError("Correction job not completed or no output file")

        from pathlib import Path
        file_path = Path(job.output_path)
        if not file_path.exists():
            raise NotFoundError("CorrectionFile", str(file_path))

        return {
            "file_path": str(file_path),
            "filename": f"corrected_{doc.original_filename if doc else 'document.docx'}",
            "is_ready": True,
        }