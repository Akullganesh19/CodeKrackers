"""User schemas with validation."""

from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from backend.models.user import UserRole


class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True
    full_name: Optional[str] = Field(None, min_length=1, max_length=256)
    role: Optional[UserRole] = UserRole.USER


class UserCreate(UserBase):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    full_name: str = Field(..., min_length=1, max_length=256)


class UserUpdate(UserBase):
    password: Optional[str] = Field(None, min_length=8, max_length=128)


class UserInDBBase(UserBase):
    id: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)


class User(UserInDBBase):
    pass
