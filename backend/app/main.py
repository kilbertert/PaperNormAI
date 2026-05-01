"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.exceptions import (
    AppException,
    app_exception_handler,
    http_exception_handler,
    DocumentNotFoundError,
    TemplateNotFoundError,
    ValidationJobNotFoundError,
    FileTypeNotSupportedError,
    DocumentProcessingError,
)
from app.api.routes import api_router

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(DocumentNotFoundError, app_exception_handler)
app.add_exception_handler(TemplateNotFoundError, app_exception_handler)
app.add_exception_handler(ValidationJobNotFoundError, app_exception_handler)
app.add_exception_handler(FileTypeNotSupportedError, app_exception_handler)
app.add_exception_handler(DocumentProcessingError, app_exception_handler)

# Include API routes
app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": settings.version}