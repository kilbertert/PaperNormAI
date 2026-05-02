"""Template entity."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID
import uuid


class DegreeType(str, Enum):
    """Academic degree type."""
    BACHELOR = "bachelor"
    MASTER = "master"
    DOCTOR = "doctor"


@dataclass
class Template:
    """Domain entity representing a university paper format template."""

    university: str
    degree_type: DegreeType
    discipline: str
    version: str = "1.0"
    id: UUID = field(default_factory=uuid.uuid4)
    rules: List = field(default_factory=list)
    file_path: Optional[str] = None
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def add_rule(self, rule) -> None:
        """Add a validation rule to this template."""
        self.rules.append(rule)
        self.updated_at = datetime.utcnow()

    def get_active_rules(self) -> List:
        """Get all active validation rules."""
        return [r for r in self.rules if getattr(r, "is_active", True)]