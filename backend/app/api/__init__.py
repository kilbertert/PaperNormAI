"""API layer package.

Contains FastAPI endpoints, request/response models, and API dependencies.
"""

from app.api.routes import api_router

__all__ = ["api_router"]