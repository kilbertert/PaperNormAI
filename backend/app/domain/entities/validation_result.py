"""ValidationResult and ValidationReport entities."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional, UUID
import uuid


class Severity(str, Enum):
    """Severity level for validation results."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationResult:
    """Domain entity representing a single validation result."""

    rule_id: str
    rule_name: str
    element_path: str
    expected_value: str
    actual_value: str
    message: str
    severity: Severity = Severity.ERROR
    auto_fixable: bool = False
    ai_enhanced: bool = False
    confidence: Optional[float] = None
    id: UUID = field(default_factory=uuid.uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ValidationSummary:
    """Summary statistics for a validation report."""
    total: int = 0
    errors: int = 0
    warnings: int = 0
    infos: int = 0
    auto_fixable: int = 0


@dataclass
class ValidationReport:
    """Domain entity representing a complete validation report."""

    document_id: UUID
    template_id: UUID
    job_id: UUID
    results: List[ValidationResult] = field(default_factory=list)
    generated_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def summary(self) -> ValidationSummary:
        """Generate summary statistics."""
        summary = ValidationSummary()
        for result in self.results:
            summary.total += 1
            if result.severity == Severity.ERROR:
                summary.errors += 1
            elif result.severity == Severity.WARNING:
                summary.warnings += 1
            elif result.severity == Severity.INFO:
                summary.infos += 1
            if result.auto_fixable:
                summary.auto_fixable += 1
        return summary