"""Document repository implementation using SQLAlchemy."""

from typing import List, Optional
from uuid import UUID
from datetime import datetime
from pathlib import Path

from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.domain.entities.document import Document, DocumentStatus
from app.domain.repositories import IDocumentRepository
from app.infrastructure.persistence.models import DocumentModel
from app.infrastructure.persistence.mappers import DocumentMapper


class DocumentRepository(IDocumentRepository):
    """SQLAlchemy implementation of DocumentRepository."""

    def __init__(self, db: Session):
        self._db = db

    def save(self, document: Document) -> None:
        """Save a document to database."""
        model = DocumentMapper.to_model(document)
        self._db.add(model)
        self._db.commit()

    def find_by_id(self, document_id: UUID) -> Optional[Document]:
        """Find a document by ID."""
        model = self._db.query(DocumentModel).filter(
            DocumentModel.id == document_id
        ).first()

        if model is None:
            return None

        return DocumentMapper.to_domain(model)

    def find_by_user_id(self, user_id: UUID, limit: int = 100, offset: int = 0) -> List[Document]:
        """Find all documents for a user."""
        models = self._db.query(DocumentModel).filter(
            DocumentModel.user_id == user_id
        ).order_by(
            desc(DocumentModel.uploaded_at)
        ).limit(limit).offset(offset).all()

        return [DocumentMapper.to_domain(m) for m in models]

    def find_by_hash(self, file_hash: str) -> Optional[Document]:
        """Find a document by file hash (for deduplication)."""
        model = self._db.query(DocumentModel).filter(
            DocumentModel.file_hash == file_hash
        ).first()

        if model is None:
            return None

        return DocumentMapper.to_domain(model)

    def update(self, document: Document) -> None:
        """Update a document."""
        model = self._db.query(DocumentModel).filter(
            DocumentModel.id == document.id
        ).first()

        if model is None:
            raise ValueError(f"Document not found: {document.id}")

        model.original_filename = document.original_filename
        model.template_id = document.template_id
        model.status = document.status.value
        model.updated_at = datetime.utcnow()

        self._db.commit()

    def delete(self, document_id: UUID) -> None:
        """Delete a document."""
        model = self._db.query(DocumentModel).filter(
            DocumentModel.id == document_id
        ).first()

        if model:
            self._db.delete(model)
            self._db.commit()

    def find_by_status(
        self,
        status: DocumentStatus,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Document]:
        """Find documents by status."""
        models = self._db.query(DocumentModel).filter(
            DocumentModel.status == status.value
        ).order_by(
            desc(DocumentModel.uploaded_at)
        ).limit(limit).offset(offset).all()

        return [DocumentMapper.to_domain(m) for m in models]

    def count_by_user(self, user_id: UUID) -> int:
        """Count documents for a user."""
        return self._db.query(DocumentModel).filter(
            DocumentModel.user_id == user_id
        ).count()