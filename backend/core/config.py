import os
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "VSDP - Vishing & Smishing Defense Platform"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "production")

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./vsdp.db")

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-super-secret-key-for-vsdp-platform")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    API_V1_STR: str = "/api"

    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    OTP_EXPIRE_SECONDS: int = 300

    # ML Config
    WHISPER_MODEL_SIZE: str = os.getenv("WHISPER_MODEL_SIZE", "base")

    # External APIs
    CYBERCRIME_PORTAL_URL: str = "https://cybercrime.gov.in/api"
    TWILIO_ACCOUNT_SID: Optional[str] = os.getenv("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN: Optional[str] = os.getenv("TWILIO_AUTH_TOKEN")
    TWILIO_PHONE_NUMBER: Optional[str] = os.getenv("TWILIO_PHONE_NUMBER")
    SENDGRID_API_KEY: Optional[str] = os.getenv("SENDGRID_API_KEY")
    FROM_EMAIL: str = os.getenv("FROM_EMAIL", "noreply@vsdp.org")
    GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")
    HONEYPOT_IS_API_KEY: Optional[str] = os.getenv("HONEYPOT_IS_API_KEY")

    # Rate Limiting
    RATE_LIMIT_DEFAULT: str = "100/minute"
    RATE_LIMIT_AUTH: str = "5/minute"

    class Config:
        env_file = ".env"


settings = Settings()
