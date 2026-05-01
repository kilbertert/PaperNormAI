"""Infrastructure DOCX parsing module."""

from app.infrastructure.docx.document_parser import DocumentParser
from app.infrastructure.docx.document_writer import DocumentWriter

__all__ = ["DocumentParser", "DocumentWriter"]