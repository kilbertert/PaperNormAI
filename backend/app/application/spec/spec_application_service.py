"""Spec application service — orchestrates spec parsing, validation, and session management."""

import hashlib
import tempfile
from pathlib import Path
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session, joinedload

from app.application.exceptions import NotFoundError, AccessDeniedError, ValidationError
from app.domain.services.rule_extraction_service import RuleExtractionService
from app.domain.services.semantic_validation_service import SemanticValidationService
from app.domain.entities.validation_report import ValidationReport
from app.domain.entities.document import DocumentStatus
from app.infrastructure.docling.parser import DoclingDocumentParser
from app.infrastructure.ai.openai_provider import OpenAIProvider
from app.infrastructure.persistence.spec_session_repository import SpecSessionRepository
from app.infrastructure.persistence.document_repository import DocumentRepository
from app.infrastructure.persistence.models import ValidationReportModel, ViolationDetailModel, DocumentModel
from app.infrastructure.storage.file_storage import FileStorage
from app.core.config import settings


# Infrastructure singletons (same as used in endpoint, moved to service level)
_parser = DoclingDocumentParser()
_ai_provider = OpenAIProvider()


class SpecApplicationService:
    """Orchestrates spec-based validation workflows."""

    def __init__(self, db: Session):
        self._db = db

    def parse_spec(self, file_path: Path, user_id: UUID) -> dict:
        """Parse spec file and extract rules.

        Args:
            file_path: Path to the spec .docx file
            user_id: UUID of the current user

        Returns:
            dict with session_id, rules_count, extraction_summary, preview_rules

        Raises:
            ValidationError: if file is not a valid .docx
        """
        if not file_path.exists() or file_path.stat().st_size == 0:
            raise ValidationError("Empty or invalid file")

        spec_doc = _parser.parse(file_path)
        rules_dicts = RuleExtractionService(
            document_parser=spec_doc, ai_provider=_ai_provider
        ).extract_rules(spec_doc)

        session_id = hashlib.sha256(file_path.read_bytes()).hexdigest()[:16]
        summary = {"total_rules": len(rules_dicts), "extraction_method": "ai"}

        SpecSessionRepository(self._db).save(
            session_id=session_id,
            user_id=str(user_id),
            rules_dicts=rules_dicts,
            summary=summary,
        )
        self._db.commit()

        return {
            "session_id": session_id,
            "rules_count": len(rules_dicts),
            "extraction_summary": summary,
            "preview_rules": rules_dicts[:10],
        }

    def validate_with_spec(
        self,
        file_path: Path,
        session_id: str,
        document_name: str,
        user_id: UUID,
    ) -> dict:
        """Validate thesis against spec rules.

        Args:
            file_path: Path to the thesis .docx file
            session_id: Spec session ID
            document_name: Original filename
            user_id: UUID of the current user

        Returns:
            dict with session_id, report_id, document_name, results counts

        Raises:
            NotFoundError: if session not found
            AccessDeniedError: if user doesn't own the session
            ValidationError: if file is invalid
        """
        # Load and validate session
        session = SpecSessionRepository(self._db).find(session_id)
        if not session:
            raise NotFoundError("SpecSession", session_id)
        if session["user_id"] != str(user_id):
            raise AccessDeniedError("SpecSession", session_id)

        if not file_path.exists() or file_path.stat().st_size == 0:
            raise ValidationError("Empty or invalid thesis file")

        # Run validation
        thesis_doc = _parser.parse(file_path)
        report = SemanticValidationService(
            document_parser=thesis_doc, ai_provider=_ai_provider
        ).validate(
            thesis_doc=thesis_doc,
            rules=session.get("rules_dicts", []),
            document_name=document_name,
            template_name="spec-based",
        )

        # Persist report
        report_id = str(report.id)
        self._persist_report(report_id, session_id, document_name, report)
        self._persist_document(file_path, report_id, document_name, user_id)

        self._db.commit()

        return {
            "session_id": session_id,
            "report_id": report_id,
            "document_name": document_name,
            "results_count": len(report.violations),
            "error_count": sum(1 for v in report.violations if v.severity.value == "error"),
            "warning_count": sum(1 for v in report.violations if v.severity.value == "warning"),
            "info_count": sum(1 for v in report.violations if v.severity.value == "info"),
        }

    def get_spec_session(self, session_id: str, user_id: UUID) -> dict:
        """Get spec session by ID.

        Args:
            session_id: Session ID
            user_id: UUID of the current user

        Returns:
            dict with session data

        Raises:
            NotFoundError: if session not found
            AccessDeniedError: if user doesn't own the session
        """
        session = SpecSessionRepository(self._db).find(session_id)
        if not session:
            raise NotFoundError("SpecSession", session_id)
        if session["user_id"] != str(user_id):
            raise AccessDeniedError("SpecSession", session_id)

        return {
            "session_id": session_id,
            "rules_count": len(session["rules_dicts"]),
            "summary": session["summary"],
        }

    def get_validation_report(self, report_id: str, user_id: UUID) -> dict:
        """Get validation report with violations.

        Args:
            report_id: Report UUID
            user_id: UUID of the current user

        Returns:
            dict with report data including violations

        Raises:
            NotFoundError: if report not found
            AccessDeniedError: if user doesn't own the report's session
        """
        report_model = (
            self._db.query(ValidationReportModel)
            .options(joinedload(ValidationReportModel.violations))
            .filter(ValidationReportModel.report_id == report_id)
            .first()
        )
        if not report_model:
            raise NotFoundError("ValidationReport", report_id)

        session = SpecSessionRepository(self._db).find(report_model.session_id)
        if not session or session["user_id"] != str(user_id):
            raise AccessDeniedError("ValidationReport", report_id)

        return {
            "report_id": report_model.report_id,
            "session_id": report_model.session_id,
            "document_name": report_model.document_name,
            "template_name": report_model.template_name,
            "created_at": report_model.created_at,
            "total_count": report_model.total_count,
            "error_count": report_model.error_count,
            "warning_count": report_model.warning_count,
            "info_count": report_model.info_count,
            "violations": [
                {
                    "id": v.id,
                    "category": v.category,
                    "severity": v.severity,
                    "description": v.description,
                    "paragraph_index": v.paragraph_index,
                    "text": v.text,
                    "original_content": v.original_content or "",
                    "suggested_fix": v.suggested_fix or "",
                    "context_before": v.context_before,
                    "context_after": v.context_after,
                    "user_modified_fix": v.user_modified_fix,
                }
                for v in report_model.violations
            ],
        }

    def delete_spec_session(self, session_id: str, user_id: UUID) -> None:
        """Delete spec session.

        Args:
            session_id: Session ID
            user_id: UUID of the current user

        Raises:
            NotFoundError: if session not found
            AccessDeniedError: if user doesn't own the session
        """
        session = SpecSessionRepository(self._db).find(session_id)
        if not session:
            raise NotFoundError("SpecSession", session_id)
        if session["user_id"] != str(user_id):
            raise AccessDeniedError("SpecSession", session_id)

        SpecSessionRepository(self._db).delete(session_id)
        self._db.commit()

    def _persist_report(
        self,
        report_id: str,
        session_id: str,
        document_name: str,
        report: ValidationReport,
    ) -> None:
        """Persist ValidationReport and ViolationDetails."""
        report_model = ValidationReportModel(
            report_id=report_id,
            session_id=session_id,
            document_name=document_name,
            template_name="spec-based",
            total_count=len(report.violations),
            error_count=sum(1 for v in report.violations if v.severity.value == "error"),
            warning_count=sum(1 for v in report.violations if v.severity.value == "warning"),
            info_count=sum(1 for v in report.violations if v.severity.value == "info"),
        )
        self._db.add(report_model)

        for v in report.violations:
            violation_id = str(v.id)
            violation_model = ViolationDetailModel(
                id=violation_id,
                report_id=report_id,
                category=v.category.value if hasattr(v.category, "value") else str(v.category),
                severity=v.severity.value if hasattr(v.severity, "value") else str(v.severity),
                description=v.description,
                paragraph_index=v.location.paragraph_index if v.location else None,
                text=v.location.text if v.location else None,
                original_content=v.original_content,
                suggested_fix=v.suggested_fix,
                context_before=v.context_before,
                context_after=v.context_after,
                user_modified_fix=v.user_modified_fix,
            )
            self._db.add(violation_model)

    def _persist_document(
        self,
        file_path: Path,
        doc_id: str,
        filename: str,
        user_id: UUID,
    ) -> None:
        """Persist thesis as DocumentModel."""
        storage = FileStorage(base_path=settings.upload_dir)
        stored_path = storage.store(file_path, doc_id)
        file_hash = self._calculate_file_hash(file_path)

        from sqlalchemy import text
        self._db.execute(
            text("""
                INSERT INTO documents (id, user_id, original_filename, file_path, file_hash, template_id, status, uploaded_at, updated_at)
                VALUES (:id, :user_id, :fn, :fp, :fh, NULL, :status, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """),
            {
                "id": doc_id,
                "user_id": str(user_id),
                "fn": filename,
                "fp": str(stored_path),
                "fh": file_hash,
                "status": DocumentStatus.COMPLETED.value,
            },
        )

    @staticmethod
    def _calculate_file_hash(file_path: Path) -> str:
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        return sha256.hexdigest()