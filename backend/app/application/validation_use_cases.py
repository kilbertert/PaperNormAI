"""Validation application use cases."""

from dataclasses import dataclass
from typing import Optional
from uuid import UUID
import uuid

from app.domain.entities.document import Document
from app.domain.entities.template import Template
from app.domain.entities.validation_result import ValidationReport
from app.domain.entities.validation_rule import RuleLevel, Severity, ValidationRule
from app.domain.services.rule_engine import RuleEngine
from app.domain.services.template_service import TemplateService
from app.application.document_use_cases import DocumentUseCases


@dataclass
class ValidationJob:
    """Represents a validation job."""
    id: UUID
    document_id: UUID
    template_id: UUID
    status: str = "pending"
    created_at: Optional = None


class ValidationUseCases:
    """Application use cases for validation operations."""

    def __init__(
        self,
        rule_engine: RuleEngine,
        template_service: TemplateService,
        document_use_cases: DocumentUseCases,
    ):
        self._rule_engine = rule_engine
        self._template_service = template_service
        self._document_use_cases = document_use_cases

    def create_validation_job(
        self,
        document_id: UUID,
        template_id: UUID,
    ) -> ValidationJob:
        """Create a new validation job.

        Args:
            document_id: The document to validate
            template_id: The template to validate against

        Returns:
            The created ValidationJob
        """
        job = ValidationJob(
            id=uuid.uuid4(),
            document_id=document_id,
            template_id=template_id,
            status="pending",
        )
        # TODO: Persist job
        return job

    def execute_validation(self, job: ValidationJob) -> ValidationReport:
        """Execute a validation job.

        Args:
            job: The validation job to execute

        Returns:
            ValidationReport with results
        """
        # Get document and template
        document = self._document_use_cases.get_document(job.document_id, user_id=None)
        if not document:
            raise ValueError(f"Document not found: {job.document_id}")

        template = self._template_service.get_template(job.template_id)
        if not template:
            raise ValueError(f"Template not found: {job.template_id}")

        # Parse document
        parsed = self._document_use_cases.parse_document(document)

        # Execute validation
        report = self._rule_engine.validate(document, parsed, template)

        return report

    def get_validation_summary(self, report: ValidationReport) -> dict:
        """Get a summary of validation results.

        Args:
            report: The validation report

        Returns:
            Summary dict with counts
        """
        summary = report.summary
        return {
            "total": summary.total,
            "errors": summary.errors,
            "warnings": summary.warnings,
            "infos": summary.infos,
            "auto_fixable": summary.auto_fixable,
        }