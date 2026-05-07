"""
Application configuration with Pydantic validation and environment variable loading.
"""
from pathlib import Path
from typing import List, Optional, Union

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=str(Path(__file__).resolve().parent.parent.parent / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ─── Application ───
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "VAS System - Vishing & Smishing Detection"
    VERSION: str = "2.1.0"
    DEBUG: bool = False

    # ─── Database ───
    DATABASE_URL: str = "sqlite:////tmp/vas.db" if Path("/var/task").exists() else "sqlite:///./vas.db"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = ""
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str = "vas_db"

    # ─── Security ───
    SECRET_KEY: str = "change-me-in-production-use-a-secure-random-key"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    ALLOWED_HOSTS: List[str] = ["*"]

    # ─── AI / Groq ───
    GROQ_API_KEY: Optional[str] = None
    GROQ_MODEL: str = "llama-3.1-8b-instant"

    # ─── Twilio ───
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_PHONE_NUMBER: Optional[str] = None

    # ─── Honeypot.is ───
    HONEYPOT_IS_API_KEY: Optional[str] = None

    # ─── CORS ───
    BACKEND_CORS_ORIGINS: Union[List[str], str] = ["http://localhost:3000"]

    # ─── Rate Limiting ───
    RATE_LIMIT_DEFAULT: str = "100/minute"
    RATE_LIMIT_AUTH: str = "5/minute"

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        return []

    @field_validator("SECRET_KEY", mode="after")
    @classmethod
    def warn_default_secret(cls, v: str) -> str:
        if v == "change-me-in-production-use-a-secure-random-key":
            import warnings
            warnings.warn(
                "⚠️  Using default SECRET_KEY! Set a strong random key in production.",
                stacklevel=2,
            )
        return v


settings = Settings()
