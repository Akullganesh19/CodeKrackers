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
from backend.models.orm import Threat, DeviceInfo
from backend.models.orm import User as ORMUser
from backend.schemas.user import UserCreate, User as UserSchema

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


@router.get("/profile")
def get_user_profile(
    db: Session = Depends(deps.get_db),
    current_user: ORMUser = Depends(deps.get_current_active_user),
) -> Any:
    """Get current user's profile with stats, recent threats, and devices."""

    # Get recent threats owned by the user
    recent_threats = (
        db.query(Threat)
        .filter(Threat.user_id == current_user.id)
        .order_by(Threat.detected_at.desc())
        .limit(10)
        .all()
    )

    # Get registered devices
    devices = (
        db.query(DeviceInfo)
        .filter(DeviceInfo.user_id == current_user.id)
        .order_by(DeviceInfo.created_at.desc())
        .limit(5)
        .all()
    )

    threats_data = []
    for t in recent_threats:
        threats_data.append(
            {
                "id": t.id,
                "type": t.type.value if hasattr(t.type, "value") else t.type,
                "severity": (
                    t.severity.value if hasattr(t.severity, "value") else t.severity
                ),
                "status": t.status,
                "detected_at": (t.detected_at.isoformat() if t.detected_at else None),
                "source_number": t.sender_id or t.caller_id,
                "confidence": t.confidence,
            }
        )

    devices_data = []
    for d in devices:
        brand = d.device_brand or ""
        model = d.device_model or ""
        os_n = d.os_name or ""
        os_v = d.os_version or ""
        dev_name = f"{brand} {model}".strip() or "Unknown"
        os_full = f"{os_n} {os_v}".strip()
        reg_at = d.created_at.isoformat() if getattr(d, "created_at", None) else None

        devices_data.append(
            {
                "id": d.id,
                "device": dev_name,
                "os": os_full,
                "ip": d.ip_address,
                "registered_at": reg_at,
            }
        )

    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": (
            current_user.role.value
            if hasattr(current_user.role, "value")
            else current_user.role
        ),
        "safety_score": current_user.safety_score,
        "scams_avoided": current_user.scams_avoided,
        "recent_threats": threats_data,
        "devices": devices_data,
    }
