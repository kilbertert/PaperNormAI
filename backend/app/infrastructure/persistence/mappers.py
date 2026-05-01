"""Mappers for converting between domain entities and database models."""

import json
from uuid import UUID
from datetime import datetime
from typing import Optional, List

from app.domain.entities.document import Document, DocumentStatus
from app.domain.entities.template import Template, DegreeType
from app.domain.entities.validation_rule import ValidationRule, RuleLevel, Severity
from app.domain.entities.validation_result import ValidationResult, ValidationReport
from app.domain.entities.correction_plan import CorrectionPlan, CorrectionStatus, CorrectionActionType

from app.infrastructure.persistence.models import (
    DocumentModel,
    TemplateModel,
    ValidationJobModel,
    ValidationResultModel,
    CorrectionPlanModel,
    UserModel,
)


class DocumentMapper:
    """Mapper for Document entity ↔ DocumentModel."""

    @staticmethod
    def to_domain(model: DocumentModel) -> Document:
        """Convert database model to domain entity."""
        return Document(
            id=model.id,
            user_id=model.user_id,
            original_filename=model.original_filename,
            file_path=model.file_path,
            file_hash=model.file_hash,
            template_id=model.template_id,
            status=DocumentStatus(model.status),
            uploaded_at=model.uploaded_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def to_model(entity: Document) -> DocumentModel:
        """Convert domain entity to database model."""
        return DocumentModel(
            id=entity.id,
            user_id=entity.user_id,
            original_filename=entity.original_filename,
            file_path=str(entity.file_path),
            file_hash=entity.file_hash,
            template_id=entity.template_id,
            status=entity.status.value,
            uploaded_at=entity.uploaded_at,
            updated_at=entity.updated_at,
        )


class TemplateMapper:
    """Mapper for Template entity ↔ TemplateModel."""

    @staticmethod
    def to_domain(model: TemplateModel) -> Template:
        """Convert database model to domain entity."""
        rules = []
        if model.rules_json:
            try:
                rules_data = json.loads(model.rules_json)
                rules = [TemplateMapper._parse_rule(r) for r in rules_data]
            except (json.JSONDecodeError, KeyError):
                pass

        return Template(
            id=model.id,
            university=model.university,
            degree_type=DegreeType(model.degree_type),
            discipline=model.discipline,
            version=model.version,
            rules=rules,
            file_path=model.file_path,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def _parse_rule(data: dict) -> ValidationRule:
        """Parse rule data into ValidationRule entity."""
        return ValidationRule(
            id=data["id"],
            name=data["name"],
            level=RuleLevel(data["level"]),
            description=data["description"],
            severity=Severity(data.get("severity", "error")),
            auto_fixable=data.get("auto_fixable", False),
            params=data.get("params", {}),
        )

    @staticmethod
    def to_model(entity: Template) -> TemplateModel:
        """Convert domain entity to database model."""
        rules_json = json.dumps([
            {
                "id": r.id,
                "name": r.name,
                "level": r.level.value,
                "description": r.description,
                "severity": r.severity.value,
                "auto_fixable": r.auto_fixable,
                "params": r.params,
            }
            for r in entity.rules
        ])

        return TemplateModel(
            id=entity.id,
            university=entity.university,
            degree_type=entity.degree_type.value,
            discipline=entity.discipline,
            version=entity.version,
            rules_json=rules_json,
            file_path=entity.file_path,
            is_active=entity.is_active,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )


class ValidationResultMapper:
    """Mapper for ValidationResult entity ↔ ValidationResultModel."""

    @staticmethod
    def to_domain(model: ValidationResultModel) -> ValidationResult:
        """Convert database model to domain entity."""
        return ValidationResult(
            id=model.id,
            rule_id=model.rule_id,
            rule_name=model.rule_name,
            element_path=model.element_path,
            expected_value=model.expected_value or "",
            actual_value=model.actual_value or "",
            message=model.message or "",
            severity=Severity(model.severity),
            auto_fixable=model.auto_fixable,
            ai_enhanced=model.ai_enhanced,
            confidence=model.confidence,
            created_at=model.created_at,
        )

    @staticmethod
    def to_model(entity: ValidationResult) -> ValidationResultModel:
        """Convert domain entity to database model."""
        return ValidationResultModel(
            id=entity.id,
            rule_id=entity.rule_id,
            rule_name=entity.rule_name,
            element_path=entity.element_path,
            severity=entity.severity.value,
            expected_value=entity.expected_value,
            actual_value=entity.actual_value,
            message=entity.message,
            auto_fixable=entity.auto_fixable,
            ai_enhanced=entity.ai_enhanced,
            confidence=entity.confidence,
            created_at=entity.created_at,
        )


class CorrectionPlanMapper:
    """Mapper for CorrectionPlan entity ↔ CorrectionPlanModel."""

    @staticmethod
    def to_domain(model: CorrectionPlanModel) -> CorrectionPlan:
        """Convert database model to domain entity."""
        return CorrectionPlan(
            id=model.id,
            result_id=model.result_id,
            action_type=CorrectionActionType(model.action_type),
            target_path=model.target_path,
            original_value=model.original_value,
            planned_value=model.planned_value,
            status=CorrectionStatus(model.status),
            applied_at=model.applied_at,
            created_at=model.created_at,
        )

    @staticmethod
    def to_model(entity: CorrectionPlan) -> CorrectionPlanModel:
        """Convert domain entity to database model."""
        return CorrectionPlanModel(
            id=entity.id,
            result_id=entity.result_id,
            action_type=entity.action_type.value,
            target_path=entity.target_path,
            original_value=entity.original_value,
            planned_value=entity.planned_value,
            status=entity.status.value,
            applied_at=entity.applied_at,
            created_at=entity.created_at,
        )