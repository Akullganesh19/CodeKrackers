"""
Child Lock Service — parental controls for calls and messages.
"""

import logging
import re
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from backend.models.orm import ChildProfile, ChildActivityLog, ChildLockMode

logger = logging.getLogger("vas.childlock")

# ─── Indian emergency numbers (always allowed) ───
EMERGENCY_NUMBERS = [
    "100",  # Police
    "101",  # Fire
    "102",  # Ambulance
    "108",  # Emergency medical
    "112",  # Universal emergency
    "1098",  # Childline
    "181",  # Women helpline
    "1091",  # Women helpline
]

# ─── Inappropriate content keywords ───
INAPPROPRIATE_KEYWORDS = [
    "drugs",
    "alcohol",
    "gambling",
    "casino",
    "betting",
    "adult",
    "xxx",
    "nude",
    "sexy",
    "gun",
    "weapon",
    "kill",
    "suicide",
    "self-harm",
    "cigarette",
    "vape",
    "weed",
    "ganja",
    "dark web",
    "darknet",
    "tor browser",
    "crypto invest",
    "bitcoin profit",
    "forex signal",
]


def check_call_allowed(
    db: Session,
    child_profile_id: str,
    phone_number: str,
) -> Dict[str, Any]:
    """
    Check if a call is allowed for a child profile.
    Returns allow/block with reason.
    """
    profile = (
        db.query(ChildProfile)
        .filter(ChildProfile.id == child_profile_id, ChildProfile.is_active == True)
        .first()
    )

    if not profile:
        return {"allowed": True, "reason": "No active child profile"}

    clean_number = re.sub(r"[\s\-()]", "", phone_number)

    # Emergency calls always allowed
    if profile.allow_emergency_calls and clean_number in EMERGENCY_NUMBERS:
        _log_activity(db, profile.id, "call_allowed", phone_number, "Emergency number")
        return {"allowed": True, "reason": "Emergency number"}

    # Emergency contacts always allowed
    if profile.emergency_contacts:
        for ec in profile.emergency_contacts:
            if re.sub(r"[\s\-()]", "", ec) in clean_number:
                _log_activity(
                    db, profile.id, "call_allowed", phone_number, "Emergency contact"
                )
                return {"allowed": True, "reason": "Emergency contact"}

    # Full lockdown — block everything except emergency
    if profile.lock_mode == ChildLockMode.FULL_LOCKDOWN:
        _log_activity(
            db, profile.id, "call_blocked", phone_number, "Full lockdown mode"
        )
        return {
            "allowed": False,
            "reason": "Full lockdown mode - only emergency calls allowed",
        }

    # Block all calls
    if profile.block_all_calls:
        _log_activity(db, profile.id, "call_blocked", phone_number, "All calls blocked")
        return {"allowed": False, "reason": "All calls are blocked on this device"}

    # Time restriction
    if profile.enforce_time_limits:
        now_time = datetime.now(timezone.utc).strftime("%H:%M")
        if not (profile.allowed_call_start <= now_time <= profile.allowed_call_end):
            _log_activity(
                db,
                profile.id,
                "call_blocked",
                phone_number,
                f"Outside allowed hours ({profile.allowed_call_start}-{profile.allowed_call_end})",
            )
            return {
                "allowed": False,
                "reason": f"Calls not allowed at this time. Allowed: {profile.allowed_call_start} - {profile.allowed_call_end}",
            }

    # Whitelist-only mode
    if profile.lock_mode == ChildLockMode.WHITELIST_ONLY:
        if profile.whitelisted_contacts:
            for wl in profile.whitelisted_contacts:
                if re.sub(r"[\s\-()]", "", wl) in clean_number:
                    _log_activity(
                        db,
                        profile.id,
                        "call_allowed",
                        phone_number,
                        "Whitelisted contact",
                    )
                    return {"allowed": True, "reason": "Whitelisted contact"}
        _log_activity(db, profile.id, "call_blocked", phone_number, "Not in whitelist")
        return {"allowed": False, "reason": "Number not in approved contacts list"}

    # Block unknown callers
    if profile.block_unknown_calls:
        if profile.whitelisted_contacts:
            is_known = any(
                re.sub(r"[\s\-()]", "", wl) in clean_number
                for wl in profile.whitelisted_contacts
            )
            if not is_known:
                _log_activity(
                    db, profile.id, "call_blocked", phone_number, "Unknown caller"
                )
                return {"allowed": False, "reason": "Unknown caller blocked"}

    # Block international
    if (
        profile.block_international_calls
        and not clean_number.startswith("+91")
        and clean_number.startswith("+")
    ):
        _log_activity(
            db, profile.id, "call_blocked", phone_number, "International call blocked"
        )
        return {"allowed": False, "reason": "International calls are blocked"}

    _log_activity(db, profile.id, "call_allowed", phone_number, "Passed all checks")
    return {"allowed": True, "reason": "Call allowed"}


def check_sms_allowed(
    db: Session,
    child_profile_id: str,
    phone_number: str,
    content: str,
) -> Dict[str, Any]:
    """
    Check if an SMS is allowed for a child profile.
    Includes content filtering for inappropriate material.
    """
    profile = (
        db.query(ChildProfile)
        .filter(ChildProfile.id == child_profile_id, ChildProfile.is_active == True)
        .first()
    )

    if not profile:
        return {
            "allowed": True,
            "reason": "No active child profile",
            "filtered_content": content,
        }

    clean_number = re.sub(r"[\s\-()]", "", phone_number)

    # Emergency contacts always allowed
    if profile.emergency_contacts:
        for ec in profile.emergency_contacts:
            if re.sub(r"[\s\-()]", "", ec) in clean_number:
                return {
                    "allowed": True,
                    "reason": "Emergency contact",
                    "filtered_content": content,
                }

    # Full lockdown
    if profile.lock_mode == ChildLockMode.FULL_LOCKDOWN:
        _log_activity(
            db, profile.id, "sms_blocked", phone_number, "Full lockdown", content[:100]
        )
        return {
            "allowed": False,
            "reason": "Full lockdown mode",
            "filtered_content": None,
        }

    # Block all SMS
    if profile.block_all_sms:
        _log_activity(
            db,
            profile.id,
            "sms_blocked",
            phone_number,
            "All SMS blocked",
            content[:100],
        )
        return {"allowed": False, "reason": "All SMS are blocked"}

    # Time restriction
    if profile.enforce_time_limits:
        now_time = datetime.now(timezone.utc).strftime("%H:%M")
        if not (profile.allowed_sms_start <= now_time <= profile.allowed_sms_end):
            _log_activity(
                db,
                profile.id,
                "sms_blocked",
                phone_number,
                "Outside hours",
                content[:100],
            )
            return {"allowed": False, "reason": f"SMS not allowed at this time"}

    # Whitelist-only
    if profile.lock_mode == ChildLockMode.WHITELIST_ONLY:
        if profile.whitelisted_contacts:
            is_whitelisted = any(
                re.sub(r"[\s\-()]", "", wl) in clean_number
                for wl in profile.whitelisted_contacts
            )
            if not is_whitelisted:
                _log_activity(
                    db,
                    profile.id,
                    "sms_blocked",
                    phone_number,
                    "Not whitelisted",
                    content[:100],
                )
                return {"allowed": False, "reason": "Sender not in approved contacts"}

    # Block URLs in SMS
    if profile.block_urls_in_sms:
        if re.search(r"https?://|www\.|bit\.ly|tinyurl", content, re.IGNORECASE):
            _log_activity(
                db,
                profile.id,
                "sms_blocked",
                phone_number,
                "Contains URL",
                content[:100],
            )
            return {
                "allowed": False,
                "reason": "Message contains a link (blocked for safety)",
            }

    # Content filtering
    filtered_content = content
    flags = []
    content_lower = content.lower()

    if profile.filter_inappropriate_content:
        for keyword in INAPPROPRIATE_KEYWORDS:
            if keyword in content_lower:
                flags.append(keyword)
                filtered_content = re.sub(
                    re.escape(keyword), "***", filtered_content, flags=re.IGNORECASE
                )

    # Custom blocked keywords
    if profile.blocked_content_keywords:
        for kw in profile.blocked_content_keywords:
            if kw.lower() in content_lower:
                flags.append(kw)
                filtered_content = re.sub(
                    re.escape(kw), "***", filtered_content, flags=re.IGNORECASE
                )

    if flags:
        _log_activity(
            db,
            profile.id,
            "sms_filtered",
            phone_number,
            f"Inappropriate content: {', '.join(flags)}",
            content[:100],
        )
        return {
            "allowed": True,
            "filtered": True,
            "reason": f"Content filtered: {', '.join(flags)}",
            "filtered_content": filtered_content,
            "flags": flags,
        }

    _log_activity(db, profile.id, "sms_allowed", phone_number, "Passed all checks")
    return {"allowed": True, "reason": "SMS allowed", "filtered_content": content}


def _log_activity(
    db: Session,
    profile_id: str,
    event: str,
    phone: str,
    reason: str,
    content: Optional[str] = None,
):
    log = ChildActivityLog(
        child_profile_id=profile_id,
        event_type=event,
        phone_number=phone,
        reason=reason[:256],
        content_snippet=(content or "")[:200],
    )
    db.add(log)
    db.commit()
