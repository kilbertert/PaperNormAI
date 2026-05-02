"""ValidationRule entity and related enums."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Dict, Any, Optional
from uuid import UUID
import uuid


class RuleLevel(str, Enum):
    """Rule classification by complexity."""
    L1 = "L1"  # Structural, deterministic
    L2 = "L2"  # Pattern-based, may need AI辅助
    L3 = "L3"  # Semantic, requires AI


class Severity(str, Enum):
    """Validation result severity."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationRule:
    """Domain entity representing a single validation rule."""

    name: str
    description: str
    level: RuleLevel
    severity: Severity = Severity.ERROR
    auto_fixable: bool = False
    params: Dict[str, Any] = field(default_factory=dict)
    check_fn: Optional[Callable] = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    is_active: bool = True

    def validate(self, document, element) -> Optional[dict]:
        """Execute the rule check function."""
        if self.check_fn and callable(self.check_fn):
            return self.check_fn(document, element, self.params)
        return None