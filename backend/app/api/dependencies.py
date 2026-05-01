"""Authentication dependencies for API endpoints."""

from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from pydantic import BaseModel

from app.core.config import settings
from app.infrastructure.persistence.user_repository import UserRepository
from app.infrastructure.persistence.models import UserModel
from app.core.database import SessionLocal

security = HTTPBearer()


class CurrentUser(BaseModel):
    """Current authenticated user."""

    id: UUID
    email: str
    role: str = "student"


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> CurrentUser:
    """Get current authenticated user from JWT token.

    Args:
        credentials: HTTP Bearer credentials

    Returns:
        CurrentUser object

    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        token = credentials.credentials
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    db = SessionLocal()
    try:
        user_repo = UserRepository(db)
        user = user_repo.find_by_id(UUID(user_id))
        if user is None:
            raise credentials_exception
        return CurrentUser(
            id=user.id,
            email=user.email,
            role=getattr(user, 'role', 'student'),
        )
    finally:
        db.close()


def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    ),
) -> Optional[CurrentUser]:
    """Get current user if authenticated, None otherwise.

    For endpoints that work both authenticated and anonymous.
    """
    if credentials is None:
        return None

    try:
        return get_current_user(credentials)
    except HTTPException:
        return None


def get_db():
    """Get database session dependency."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()