"""Document application use cases."""

from pathlib import Path
from typing import Optional
from uuid import UUID
import hashlib

from app.domain.entities.document import Document, DocumentStatus
from app.domain.repositories import IDocumentRepository
from app.infrastructure.docx.document_parser import DocumentParser
from app.infrastructure.storage.file_storage import FileStorage


class DocumentUseCases:
    """Application use cases for document operations."""

    def __init__(
        self,
        document_repository: IDocumentRepository,
        document_parser: DocumentParser,
        file_storage: FileStorage,
    ):
        self._repo = document_repository
        self._parser = document_parser
        self._storage = file_storage

    def upload_document(
        self,
        user_id: UUID,
        file_path: Path,
        original_filename: str,
        template_id: Optional[UUID] = None,
    ) -> Document:
        """Upload and register a new document.

        Args:
            user_id: The user's ID
            file_path: Path to the uploaded file
            original_filename: Original filename
            template_id: Optional template ID to attach

        Returns:
            The created Document entity
        """
        # Calculate file hash for deduplication
        file_hash = self._calculate_hash(file_path)

        # Create document entity
        document = Document(
            user_id=user_id,
            original_filename=original_filename,
            file_path=file_path,
            file_hash=file_hash,
            template_id=template_id,
        )

        # Save to storage
        self._storage.store(file_path, str(document.id))

        # Persist entity
        self._repo.save(document)

        return document

    def get_document(self, document_id: UUID, user_id: UUID) -> Optional[Document]:
        """Get a document by ID, verifying ownership."""
        document = self._repo.find_by_id(document_id)
        if document and document.user_id != user_id:
            return None
        return document

    def list_user_documents(self, user_id: UUID) -> list:
        """List all documents for a user."""
        return self._repo.find_by_user_id(user_id)

    def parse_document(self, document: Document):
        """Parse a document into intermediate model.

        Returns ParsedDocument
        """
        return self._parser.parse(document.file_path)

    def _calculate_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file."""
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        return sha256.hexdigest()