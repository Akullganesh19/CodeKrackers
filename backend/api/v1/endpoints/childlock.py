"""
Child Lock API — parental controls for calls and messages.
"""
import logging
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.api import deps
from backend.models.childlock import ChildActivityLog, ChildLockMode, ChildProfile
from backend.models.user import User
from backend.services.childlock import check_call_allowed, check_sms_allowed

logger = logging.getLogger("vas.childlock_api")
router = APIRouter()


@router.post("/profile")
def create_child_profile(
    body: dict,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """Create a child profile with parental controls."""
    name = body.get("child_name", "").strip()
    if not name:
        raise HTTPException(status_code=422, detail="child_name is required")

    try:
        mode = ChildLockMode(body.get("lock_mode", "filtered"))
    except ValueError:
        raise HTTPException(status_code=422, detail=f"Invalid lock_mode. Options: {[m.value for m in ChildLockMode]}")

    profile = ChildProfile(
        parent_id=current_user.id,
        child_name=name,
        child_age=body.get("child_age"),
        lock_mode=mode,
        block_unknown_calls=body.get("block_unknown_calls", True),
        block_international_calls=body.get("block_international_calls", True),
        block_unknown_sms=body.get("block_unknown_sms", True),
        filter_inappropriate_content=body.get("filter_inappropriate_content", True),
        block_urls_in_sms=body.get("block_urls_in_sms", True),
        enforce_time_limits=body.get("enforce_time_limits", True),
        allowed_call_start=body.get("allowed_call_start", "08:00"),
        allowed_call_end=body.get("allowed_call_end", "21:00"),
        allowed_sms_start=body.get("allowed_sms_start", "08:00"),
        allowed_sms_end=body.get("allowed_sms_end", "21:00"),
        whitelisted_contacts=body.get("whitelisted_contacts", []),
        emergency_contacts=body.get("emergency_contacts", [current_user.email]),
        blocked_content_keywords=body.get("blocked_content_keywords"),
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)

    logger.info("CHILD_PROFILE_CREATED id=%d parent=%d name=%s mode=%s", profile.id, current_user.id, name, mode.value)
    return {"id": profile.id, "child_name": name, "lock_mode": mode.value, "message": "Child profile created"}


@router.get("/profiles")
def list_child_profiles(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """List all child profiles for the current parent."""
    profiles = db.query(ChildProfile).filter(ChildProfile.parent_id == current_user.id).all()
    return [
        {
            "id": p.id,
            "child_name": p.child_name,
            "child_age": p.child_age,
            "lock_mode": p.lock_mode.value if hasattr(p.lock_mode, 'value') else p.lock_mode,
            "is_active": p.is_active,
            "block_unknown_calls": p.block_unknown_calls,
            "block_urls_in_sms": p.block_urls_in_sms,
            "allowed_hours": f"{p.allowed_call_start}-{p.allowed_call_end}",
            "whitelisted_contacts": len(p.whitelisted_contacts or []),
        }
        for p in profiles
    ]


@router.post("/check/call")
def check_child_call(
    body: dict,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """Check if a call is allowed for a child profile."""
    profile_id = body.get("profile_id")
    phone = body.get("phone_number", "")
    if not profile_id or not phone:
        raise HTTPException(status_code=422, detail="profile_id and phone_number required")

    # Verify parent owns this profile
    profile = db.query(ChildProfile).filter(ChildProfile.id == profile_id, ChildProfile.parent_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Child profile not found")

    return check_call_allowed(db, profile_id, phone)


@router.post("/check/sms")
def check_child_sms(
    body: dict,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """Check if an SMS is allowed + filter content for a child profile."""
    profile_id = body.get("profile_id")
    phone = body.get("phone_number", "")
    content = body.get("content", "")
    if not profile_id or not phone:
        raise HTTPException(status_code=422, detail="profile_id and phone_number required")

    profile = db.query(ChildProfile).filter(ChildProfile.id == profile_id, ChildProfile.parent_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Child profile not found")

    return check_sms_allowed(db, profile_id, phone, content)


@router.put("/profile/{profile_id}")
def update_child_profile(
    profile_id: int,
    body: dict,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """Update child profile settings."""
    profile = db.query(ChildProfile).filter(ChildProfile.id == profile_id, ChildProfile.parent_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Child profile not found")

    updatable = [
        "lock_mode", "is_active", "block_all_calls", "block_unknown_calls",
        "block_international_calls", "block_all_sms", "block_unknown_sms",
        "filter_inappropriate_content", "block_urls_in_sms", "enforce_time_limits",
        "allowed_call_start", "allowed_call_end", "allowed_sms_start", "allowed_sms_end",
        "whitelisted_contacts", "emergency_contacts", "blocked_content_keywords",
    ]
    for field in updatable:
        if field in body:
            if field == "lock_mode":
                setattr(profile, field, ChildLockMode(body[field]))
            else:
                setattr(profile, field, body[field])

    db.commit()
    logger.info("CHILD_PROFILE_UPDATED id=%d by=%d", profile_id, current_user.id)
    return {"message": "Child profile updated", "id": profile_id}


@router.get("/activity/{profile_id}")
def get_child_activity(
    profile_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """Get activity log for a child profile (what was blocked/allowed)."""
    profile = db.query(ChildProfile).filter(ChildProfile.id == profile_id, ChildProfile.parent_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Child profile not found")

    logs = (
        db.query(ChildActivityLog)
        .filter(ChildActivityLog.child_profile_id == profile_id)
        .order_by(ChildActivityLog.timestamp.desc())
        .limit(100)
        .all()
    )
    return [
        {
            "event": l.event_type,
            "phone": l.phone_number,
            "reason": l.reason,
            "content": l.content_snippet,
            "timestamp": l.timestamp.isoformat() if l.timestamp else None,
        }
        for l in logs
    ]
