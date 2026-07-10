import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserRole(str, Enum):
    CITIZEN = "citizen"
    USER = "user"
    OFFICER = "officer"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


# Base schema for common user attributes


class UserBase(BaseModel):
    email: EmailStr
    phone: Optional[str] = None
    full_name: Optional[str] = None
    role: str = "citizen"  # Default role
    rbac_level: int = 1  # Default RBAC level
    is_active: bool = True
    safety_score: float = 100.0
    scams_avoided: int = 0

    class Config:
        from_attributes = True  # Enable ORM mode for SQLAlchemy compatibility


# Schema for user creation (includes password)


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


# Schema for updating user information


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    # Add other updatable fields as needed, but exclude sensitive ones like password directly


# Schema for user response (excludes hashed_password)


class UserResponse(UserBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


# Schema for login request


class UserLogin(BaseModel):
    email: EmailStr
    password: str


# Schema for token response


class Token(BaseModel):
    access_token: str
    token_type: str


# Schema for token data (payload inside JWT)


class TokenData(BaseModel):
    user_id: Optional[uuid.UUID] = None
