"""Global exception handlers for API layer."""

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from typing import Union


class AppException(Exception):
    """Base application exception."""

    def __init__(self, message: str, code: str):
        self.message = message
        self.code = code


class DocumentNotFoundError(AppException):
    """Raised when document is not found."""

    def __init__(self, document_id: Union[str, None] = None):
        msg = f"Document not found: {document_id}" if document_id else "Document not found"
        super().__init__(msg, "DOCUMENT_NOT_FOUND")


class TemplateNotFoundError(AppException):
    """Raised when template is not found."""

    def __init__(self, template_id: Union[str, None] = None):
        msg = f"Template not found: {template_id}" if template_id else "Template not found"
        super().__init__(msg, "TEMPLATE_NOT_FOUND")


class ValidationJobNotFoundError(AppException):
    """Raised when validation job is not found."""

    def __init__(self, job_id: Union[str, None] = None):
        msg = f"Validation job not found: {job_id}" if job_id else "Validation job not found"
        super().__init__(msg, "VALIDATION_JOB_NOT_FOUND")


class FileTypeNotSupportedError(AppException):
    """Raised when file type is not supported."""

    def __init__(self, file_type: str):
        super().__init__(f"File type not supported: {file_type}", "FILE_TYPE_NOT_SUPPORTED")


class DocumentProcessingError(AppException):
    """Raised when document processing fails."""

    def __init__(self, reason: str):
        super().__init__(f"Document processing failed: {reason}", "DOCUMENT_PROCESSING_ERROR")


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handle AppException and return structured error response."""
    return JSONResponse(
        status_code=400,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": {},
            }
        },
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTPException and return structured error response."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": "HTTP_ERROR",
                "message": exc.detail,
                "details": {},
            }
        },
    )