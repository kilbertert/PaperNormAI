"""Authentication endpoints."""

from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.api.dependencies import get_db, get_current_user, CurrentUser
from app.core.config import settings
from app.infrastructure.persistence.user_repository import UserRepository
from app.infrastructure.persistence.models import UserModel

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    nickname: Optional[str] = None


class UserResponse(BaseModel):
    id: str
    email: str
    nickname: Optional[str] = None
    role: str = "student"
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    expires_in: int


class TokenData(BaseModel):
    user_id: Optional[str] = None


class LoginRequest(BaseModel):
    email: str
    password: str


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.access_token_expire_minutes
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.secret_key, algorithm=settings.algorithm
    )
    return encoded_jwt


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    repo = UserRepository(db)

    if repo.exists_by_email(user.email):
        raise HTTPException(
            status_code=400,
            detail="Email already registered",
        )

    hashed_password = get_password_hash(user.password)
    new_user = UserModel(
        email=user.email.lower(),
        password_hash=hashed_password,
        nickname=user.nickname,
        role="student",
    )

    repo.save(new_user)

    return UserResponse(
        id=str(new_user.id),
        email=new_user.email,
        nickname=new_user.nickname,
        role=new_user.role,
        created_at=new_user.created_at or datetime.utcnow(),
    )


@router.post("/login", response_model=Token)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate user and return access token."""
    repo = UserRepository(db)

    user_model = repo.find_by_email(request.email)
    if user_model is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(request.password, user_model.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": str(user_model.id)},
    )

    return Token(
        access_token=access_token,
        token_type="Bearer",
        expires_in=settings.access_token_expire_minutes * 60,
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get current user information."""
    repo = UserRepository(db)
    user_model = repo.find_by_id(current_user.id)

    if user_model is None:
        raise HTTPException(status_code=404, detail="User not found")

    return UserResponse(
        id=str(user_model.id),
        email=user_model.email,
        nickname=user_model.nickname,
        role=user_model.role,
        created_at=user_model.created_at,
    )