"""
User management endpoints with password policy and RBAC.
"""
import logging
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.api import deps
from backend.core import security
from backend.models import User, UserRole
from backend.schemas.user import UserCreate, User as UserSchema
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

logger = logging.getLogger("vas.users")
router = APIRouter()


@router.post("/", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def create_user(
    *,
    db: AsyncSession = Depends(deps.get_db),
    user_in: UserCreate,
) -> Any:
    """Create new user with password policy enforcement."""
    # Check duplicate
    result = await db.execute(select(User).where(User.email == user_in.email))
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists.",
        )

    # Enforce password policy
    is_valid, message = security.validate_password_strength(user_in.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=message,
        )

    user = User(
        email=user_in.email,
        hashed_password=security.get_password_hash(user_in.password),
        full_name=user_in.full_name,
        role=user_in.role or UserRole.USER,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    logger.info("USER_CREATED email=%s role=%s", user.email, user.role.value)
    return user


@router.get("/me", response_model=UserSchema)
def read_user_me(
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """Get current authenticated user profile."""
    return current_user


@router.get("/", response_model=List[UserSchema])
async def list_users(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """List all users (admin only)."""
    result = await db.execute(select(User).offset(skip).limit(min(limit, 100)))
    return result.scalars().all()


@router.put("/me/password")
async def change_password(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    body: dict,
) -> Any:
    """Change current user's password."""
    old_password = body.get("old_password", "")
    new_password = body.get("new_password", "")

    if not security.verify_password(old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password",
        )

    is_valid, message = security.validate_password_strength(new_password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=message,
        )

    current_user.hashed_password = security.get_password_hash(new_password)
    await db.commit()

    logger.info("PASSWORD_CHANGED user=%d", current_user.id)
    return {"message": "Password updated successfully"}
