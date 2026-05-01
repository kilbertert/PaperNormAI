"""Application configuration.

Uses environment variables with pydantic-settings for type-safe configuration.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # App
    app_name: str = "PaperNormAI"
    debug: bool = False
    version: str = "0.1.0"

    # API
    api_v1_prefix: str = "/api/v1"

    # Database
    database_url: str = "sqlite:///./paper_norm_ai.db"

    # File Storage
    upload_dir: Path = Path("./uploads")
    max_upload_size: int = 50 * 1024 * 1024  # 50MB

    # AI Service
    ai_provider: str = "openai"  # openai / local
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"
    ai_timeout: int = 30

    # JWT Auth
    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440  # 24 hours

    # CORS
    cors_origins: list[str] = ["http://localhost:3000"]


settings = Settings()