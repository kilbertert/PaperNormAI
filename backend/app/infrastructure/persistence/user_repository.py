"""User repository implementation using SQLAlchemy."""

from typing import Optional
from uuid import UUID
from datetime import datetime

from sqlalchemy.orm import Session

from app.domain.repositories import IUserRepository
from app.infrastructure.persistence.models import UserModel


class UserRepository(IUserRepository):
    """SQLAlchemy implementation of UserRepository."""

    def __init__(self, db: Session):
        self._db = db

    def save(self, user) -> None:
        """Save a user to database."""
        self._db.add(user)
        self._db.commit()

    def find_by_id(self, user_id: UUID):
        """Find a user by ID."""
        return self._db.query(UserModel).filter(
            UserModel.id == user_id
        ).first()

    def find_by_email(self, email: str):
        """Find a user by email."""
        return self._db.query(UserModel).filter(
            UserModel.email == email.lower()
        ).first()

    def update(self, user) -> None:
        """Update a user."""
        self._db.commit()

    def exists_by_email(self, email: str) -> bool:
        """Check if user exists by email."""
        return self._db.query(UserModel).filter(
            UserModel.email == email.lower()
        ).count() > 0