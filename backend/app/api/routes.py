"""API routes package."""

from fastapi import APIRouter
from app.api.endpoints import documents, templates, validations, corrections, auth

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(templates.router, prefix="/templates", tags=["templates"])
api_router.include_router(validations.router, prefix="/validations", tags=["validations"])
api_router.include_router(corrections.router, prefix="/corrections", tags=["corrections"])