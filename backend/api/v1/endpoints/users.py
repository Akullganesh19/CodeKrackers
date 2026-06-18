"""
User management endpoints with password policy and RBAC.
"""
import logging
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.api import deps
from backend.core import security
from backend.models.user import User, UserRole
from backend.schemas.user import User as UserSchema
from backend.schemas.user import UserCreate

logger = logging.getLogger("vas.users")
router = APIRouter()


@router.post("/", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
def create_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: UserCreate,
) -> Any:
    """Create new user with password policy enforcement."""
    # Check duplicate
    existing = db.query(User).filter(User.email == user_in.email).first()
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
        role=user_in.role or UserRole.CITIZEN,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    logger.info("USER_CREATED email=%s role=%s", user.email, user.role.value)
    return user


@router.get("/me", response_model=UserSchema)
def read_user_me(
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """Get current authenticated user profile."""
    return current_user


@router.get("/", response_model=List[UserSchema])
def list_users(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """List all users (admin only)."""
    return db.query(User).offset(skip).limit(min(limit, 100)).all()


@router.put("/me/password")
def change_password(
    *,
    db: Session = Depends(deps.get_db),
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
    db.commit()

    logger.info("PASSWORD_CHANGED user=%d", current_user.id)
    return {"message": "Password updated successfully"}
