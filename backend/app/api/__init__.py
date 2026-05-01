"""API layer package.

Contains FastAPI endpoints, request/response models, and API dependencies.
"""

from app.api.routes import router

__all__ = ["router"]