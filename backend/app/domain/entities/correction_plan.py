"""CorrectionPlan entity."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Any, UUID
import uuid


class CorrectionActionType(str, Enum):
    """Type of correction action."""
    REPLACE_STYLE = "replace_style"
    ADJUST_SPACING = "adjust_spacing"
    NORMALIZE_CITATION = "normalize_citation"
    FIX_FONT = "fix_font"
    FIX_LINE_SPACING = "fix_line_spacing"


class CorrectionStatus(str, Enum):
    """Correction plan status."""
    PLANNED = "planned"
    APPROVED = "approved"
    APPLIED = "applied"
    SKIPPED = "skipped"


@dataclass
class CorrectionPlan:
    """Domain entity representing an automatic correction plan."""

    result_id: UUID
    action_type: CorrectionActionType
    target_path: str
    original_value: Any
    planned_value: Any
    id: UUID = field(default_factory=uuid.uuid4)
    status: CorrectionStatus = CorrectionStatus.PLANNED
    created_at: datetime = field(default_factory=datetime.utcnow)
    applied_at: Optional[datetime] = None
    rollback_data: Optional[dict] = None

    def approve(self) -> None:
        """Approve this correction plan."""
        self.status = CorrectionStatus.APPROVED

    def apply(self) -> None:
        """Mark as applied."""
        self.status = CorrectionStatus.APPLIED
        self.applied_at = datetime.utcnow()

    def skip(self) -> None:
        """Skip this correction plan."""
        self.status = CorrectionStatus.SKIPPED