"""Document entity and related value objects."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional
from uuid import UUID
import uuid


class DocumentStatus(str, Enum):
    """Document processing status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Document:
    """Domain entity representing a user's uploaded document."""

    user_id: UUID
    original_filename: str
    file_path: Path
    file_hash: str
    id: UUID = field(default_factory=uuid.uuid4)
    template_id: Optional[UUID] = None
    status: DocumentStatus = DocumentStatus.PENDING
    uploaded_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def attach_template(self, template_id: UUID) -> None:
        """Attach a template to this document."""
        self.template_id = template_id
        self.updated_at = datetime.utcnow()

    def mark_processing(self) -> None:
        """Mark document as being processed."""
        self.status = DocumentStatus.PROCESSING
        self.updated_at = datetime.utcnow()

    def mark_completed(self) -> None:
        """Mark document as successfully processed."""
        self.status = DocumentStatus.COMPLETED
        self.updated_at = datetime.utcnow()

    def mark_failed(self) -> None:
        """Mark document as failed."""
        self.status = DocumentStatus.FAILED
        self.updated_at = datetime.utcnow()