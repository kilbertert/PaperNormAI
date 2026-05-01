"""Document management endpoints."""

from pathlib import Path
from typing import Optional
import tempfile
import hashlib

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, status
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db, CurrentUser
from app.core.config import settings
from app.infrastructure.persistence.document_repository import DocumentRepository
from app.infrastructure.docx.document_parser import DocumentParser
from app.infrastructure.storage.file_storage import FileStorage

router = APIRouter()


class DocumentResponse(BaseModel):
    id: str
    original_filename: str
    file_hash: str
    status: str
    template_id: Optional[str] = None
    uploaded_at: str


class DocumentListResponse(BaseModel):
    items: list[DocumentResponse]
    total: int
    page: int
    page_size: int


class DocumentDetailResponse(BaseModel):
    id: str
    original_filename: str
    file_hash: str
    status: str
    template_id: Optional[str] = None
    file_path: str
    word_count: Optional[int] = None
    uploaded_at: str
    updated_at: str


def _calculate_file_hash(file_path: Path) -> str:
    """Calculate SHA256 hash of a file."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


@router.post("/upload", response_model=DocumentResponse, status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    template_id: Optional[str] = Query(None),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Upload a .docx document.

    Args:
        file: The .docx file to upload
        template_id: Optional template ID to attach
        current_user: Authenticated user
        db: Database session

    Returns:
        Document metadata
    """
    if not file.filename or not file.filename.endswith(".docx"):
        raise HTTPException(
            status_code=422,
            detail="Only .docx files are supported",
        )

    if file.size and file.size > settings.max_upload_size:
        raise HTTPException(
            status_code=413,
            detail=f"File size exceeds maximum of {settings.max_upload_size} bytes",
        )

    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp_file:
        content = await file.read()
        tmp_file.write(content)
        tmp_path = Path(tmp_file.name)

    try:
        file_hash = _calculate_file_hash(tmp_path)

        doc_repo = DocumentRepository(db)
        existing = doc_repo.find_by_hash(file_hash)
        if existing and existing.user_id == current_user.id:
            return DocumentResponse(
                id=str(existing.id),
                original_filename=file.filename,
                file_hash=file_hash,
                status=existing.status.value,
                template_id=str(existing.template_id) if existing.template_id else None,
                uploaded_at=existing.uploaded_at.isoformat(),
            )

        storage = FileStorage(base_path=settings.upload_dir)
        doc_repo_instance = DocumentRepository(db)

        from app.domain.entities.document import Document, DocumentStatus
        from uuid import UUID

        document = Document(
            user_id=current_user.id,
            original_filename=file.filename,
            file_path=tmp_path,
            file_hash=file_hash,
            template_id=UUID(template_id) if template_id else None,
            status=DocumentStatus.PENDING,
        )

        stored_path = storage.store(tmp_path, str(document.id))
        document.file_path = stored_path

        doc_repo_instance.save(document)

        return DocumentResponse(
            id=str(document.id),
            original_filename=document.original_filename,
            file_hash=document.file_hash,
            status=document.status.value,
            template_id=str(document.template_id) if document.template_id else None,
            uploaded_at=document.uploaded_at.isoformat(),
        )

    finally:
        if tmp_path.exists():
            tmp_path.unlink()


@router.get("/", response_model=DocumentListResponse)
async def list_documents(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List user's documents with pagination.

    Args:
        page: Page number (1-indexed)
        page_size: Items per page
        status_filter: Optional status filter
        current_user: Authenticated user
        db: Database session

    Returns:
        Paginated list of documents
    """
    doc_repo = DocumentRepository(db)
    offset = (page - 1) * page_size

    if status_filter:
        from app.domain.entities.document import DocumentStatus
        docs = doc_repo.find_by_status(
            DocumentStatus(status_filter),
            limit=page_size,
            offset=offset,
        )
        total = len(docs)
    else:
        docs = doc_repo.find_by_user_id(
            current_user.id,
            limit=page_size,
            offset=offset,
        )
        total = doc_repo.count_by_user(current_user.id)

    items = [
        DocumentResponse(
            id=str(doc.id),
            original_filename=doc.original_filename,
            file_hash=doc.file_hash,
            status=doc.status.value,
            template_id=str(doc.template_id) if doc.template_id else None,
            uploaded_at=doc.uploaded_at.isoformat(),
        )
        for doc in docs
    ]

    return DocumentListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{document_id}", response_model=DocumentDetailResponse)
async def get_document(
    document_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get document details by ID.

    Args:
        document_id: Document UUID
        current_user: Authenticated user
        db: Database session

    Returns:
        Document details
    """
    from uuid import UUID

    doc_repo = DocumentRepository(db)

    try:
        document = doc_repo.find_by_id(UUID(document_id))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid document ID format")

    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    if document.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    return DocumentDetailResponse(
        id=str(document.id),
        original_filename=document.original_filename,
        file_hash=document.file_hash,
        status=document.status.value,
        template_id=str(document.template_id) if document.template_id else None,
        file_path=str(document.file_path),
        uploaded_at=document.uploaded_at.isoformat(),
        updated_at=document.updated_at.isoformat(),
    )


@router.get("/{document_id}/download")
async def download_document(
    document_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Download a document file.

    Args:
        document_id: Document UUID
        current_user: Authenticated user
        db: Database session

    Returns:
        FileResponse with the .docx file
    """
    from uuid import UUID

    doc_repo = DocumentRepository(db)

    try:
        document = doc_repo.find_by_id(UUID(document_id))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid document ID format")

    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    if document.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    file_path = Path(document.file_path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found on storage")

    return FileResponse(
        path=file_path,
        filename=document.original_filename,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )


@router.delete("/{document_id}", status_code=204)
async def delete_document(
    document_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a document.

    Args:
        document_id: Document UUID
        current_user: Authenticated user
        db: Database session
    """
    from uuid import UUID

    doc_repo = DocumentRepository(db)

    try:
        document = doc_repo.find_by_id(UUID(document_id))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid document ID format")

    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    if document.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    storage = FileStorage(base_path=settings.upload_dir)
    storage.delete(document_id)

    doc_repo.delete(UUID(document_id))