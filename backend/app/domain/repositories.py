"""Repository interfaces (ports) for domain layer.

These interfaces define the contract that infrastructure layer must implement.
This follows the Dependency Inversion Principle: Domain defines interfaces,
Infrastructure implements them.
"""

from typing import Protocol, Optional, List
from uuid import UUID
from app.domain.entities.document import Document
from app.domain.entities.template import Template


class IDocumentRepository(Protocol):
    """Repository interface for Document entity."""

    def save(self, document: Document) -> None:
        """Save a document."""
        ...

    def find_by_id(self, document_id: UUID) -> Optional[Document]:
        """Find a document by ID."""
        ...

    def find_by_user_id(self, user_id: UUID) -> List[Document]:
        """Find all documents for a user."""
        ...

    def update(self, document: Document) -> None:
        """Update a document."""
        ...

    def delete(self, document_id: UUID) -> None:
        """Delete a document."""
        ...


class ITemplateRepository(Protocol):
    """Repository interface for Template entity."""

    def save(self, template: Template) -> None:
        """Save a template."""
        ...

    def find_by_id(self, template_id: UUID) -> Optional[Template]:
        """Find a template by ID."""
        ...

    def find_by_university(
        self, university: str, degree_type: Optional[str] = None
    ) -> List[Template]:
        """Find templates by university."""
        ...

    def find_active(self) -> List[Template]:
        """Find all active templates."""
        ...

    def update(self, template: Template) -> None:
        """Update a template."""
        ...


class IUserRepository(Protocol):
    """Repository interface for User entity."""

    def save(self, user) -> None:
        """Save a user."""
        ...

    def find_by_id(self, user_id: UUID):
        """Find a user by ID."""
        ...

    def find_by_email(self, email: str):
        """Find a user by email."""
        ...

    def update(self, user) -> None:
        """Update a user."""
        ...