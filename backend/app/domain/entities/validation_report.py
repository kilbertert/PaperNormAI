"""ValidationReport and related entities for AI semantic validation."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID, uuid4


class ViolationSeverity(str, Enum):
    """Violation severity levels."""
    ERROR = "error"       # Must be fixed
    WARNING = "warning"  # Recommended to fix
    INFO = "info"         # Informational


class ViolationCategory(str, Enum):
    """Violation categories for Phase 1 formatting issues."""
    FONT = "font"                    # Font family
    FONT_SIZE = "font_size"          # Font size
    LINE_SPACING = "line_spacing"   # Line spacing
    PARAGRAPH_SPACING = "paragraph_spacing"  # Paragraph spacing (before/after)
    PAGE_MARGIN = "page_margin"      # Page margins
    HEADING = "heading"              # Heading levels
    # Phase 2 (not yet implemented)
    TABLE = "table"
    FORMULA = "formula"
    FIGURE = "figure"
    REFERENCE = "reference"


@dataclass
class TextLocation:
    """Text location for identifying position in document."""
    paragraph_index: int      # Paragraph index
    text: str                 # The paragraph text (for verification)
    start_offset: Optional[int] = None   # Character start offset in text
    end_offset: Optional[int] = None     # Character end offset in text


@dataclass
class ViolationDetail:
    """Single violation detail."""

    # Basic violation info (no defaults - must be provided)
    category: ViolationCategory
    severity: ViolationSeverity
    description: str                          # Violation description

    # Location info
    location: TextLocation

    # Original vs suggested fix
    original_content: str                      # Original content
    suggested_fix: str                         # Suggested fix

    # Optional fields with defaults
    id: UUID = field(default_factory=uuid4)
    user_modified_fix: Optional[str] = None
    context_before: Optional[str] = None       # Paragraph before violation
    context_after: Optional[str] = None       # Paragraph after violation


@dataclass
class ValidationReport:
    """Complete validation report."""

    # Report metadata (no defaults - must be provided)
    document_name: str                         # Document being validated
    template_name: Optional[str] = None       # Template/spec source name

    # Optional fields with defaults
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)

    # Violation list
    violations: List[ViolationDetail] = field(default_factory=list)

    # Summary statistics
    total_violations: int = 0
    error_count: int = 0
    warning_count: int = 0
    info_count: int = 0
    status: str = "pending"   # pending, reviewed, confirmed, applied

    def add_violation(self, violation: ViolationDetail) -> None:
        """Add a violation and recalculate stats."""
        self.violations.append(violation)
        self._recalc_stats()

    def _recalc_stats(self) -> None:
        self.total_violations = len(self.violations)
        self.error_count = sum(1 for v in self.violations if v.severity == ViolationSeverity.ERROR)
        self.warning_count = sum(1 for v in self.violations if v.severity == ViolationSeverity.WARNING)
        self.info_count = sum(1 for v in self.violations if v.severity == ViolationSeverity.INFO)

    def get_violation_count(self) -> int:
        """Get total violation count."""
        return len(self.violations)

    def get_error_count(self) -> int:
        """Get error count."""
        return sum(1 for v in self.violations if v.severity == ViolationSeverity.ERROR)

    def get_warning_count(self) -> int:
        """Get warning count."""
        return sum(1 for v in self.violations if v.severity == ViolationSeverity.WARNING)

    def get_info_count(self) -> int:
        """Get info count."""
        return sum(1 for v in self.violations if v.severity == ViolationSeverity.INFO)

    def get_effective_fix(self, violation_id: UUID) -> str:
        """Get effective fix (user modified takes priority over AI suggested)."""
        for v in self.violations:
            if v.id == violation_id:
                return v.user_modified_fix or v.suggested_fix
        raise ValueError(f"Violation {violation_id} not found")

    def confirm_all(self) -> None:
        """Mark all violations as confirmed."""
        self.status = "confirmed"

    def get_editable_violations(self) -> List[ViolationDetail]:
        """Get violations that have editable fixes."""
        return [v for v in self.violations if v.user_modified_fix is not None or v.suggested_fix is not None]
