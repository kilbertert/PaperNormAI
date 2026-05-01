"""Domain entities package."""

from app.domain.entities.document import Document, DocumentStatus
from app.domain.entities.template import Template, DegreeType
from app.domain.entities.validation_rule import ValidationRule, RuleLevel, Severity
from app.domain.entities.validation_result import ValidationResult, ValidationReport
from app.domain.entities.correction_plan import CorrectionPlan, CorrectionStatus, CorrectionActionType

__all__ = [
    "Document",
    "DocumentStatus",
    "Template",
    "DegreeType",
    "ValidationRule",
    "RuleLevel",
    "Severity",
    "ValidationResult",
    "ValidationReport",
    "CorrectionPlan",
    "CorrectionStatus",
    "CorrectionActionType",
]