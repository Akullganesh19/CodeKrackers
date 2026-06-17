"""
Spam Shield API — report, check, configure spam filtering.
"""
import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.api import deps
from backend.models.spam import SpamFilter, SpamReport, SpamLog, SpamType
from backend.models.user import User
from backend.services.spam_shield import check_spam

logger = logging.getLogger("vas.spam_api")
router = APIRouter()


@router.post("/check")
def spam_check(
    body: dict,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """Real-time spam check for incoming call or SMS."""
    phone = body.get("phone_number", "").strip()
    stype = body.get("type", "sms")
    content = body.get("content")

    if not phone:
        raise HTTPException(status_code=422, detail="phone_number is required")

    try:
        spam_type = SpamType(stype)
    except ValueError:
        raise HTTPException(status_code=422, detail="type must be 'call' or 'sms'")

    return check_spam(db, phone, current_user.id, spam_type, content)

@router.post("/check/live")
def spam_check_live(
    body: dict,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """Mid-call re-scoring triggered by live Whisper transcription."""
    phone = body.get("phone_number", "").strip()
    transcript = body.get("transcript")

    if not phone or not transcript:
        raise HTTPException(status_code=422, detail="phone_number and transcript required")

    return check_spam(db, phone, current_user.id, SpamType.CALL, transcript)


@router.post("/report")
def report_spam(
    body: dict,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """Report a number as spam."""
    phone = body.get("phone_number", "").strip()
    stype = body.get("type", "sms")
    content = body.get("content")
    category = body.get("category", "unknown")

    if not phone:
        raise HTTPException(status_code=422, detail="phone_number required")

    report = SpamReport(
        reporter_id=current_user.id,
        phone_number=phone,
        spam_type=SpamType(stype),
        content=(content or "")[:2000],
        category=category,
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    total_reports = db.query(SpamReport).filter(SpamReport.phone_number == phone).count()
    logger.info("SPAM_REPORTED phone=%s by=%d total=%d", phone, current_user.id, total_reports)

    return {"id": report.id, "phone_number": phone, "total_reports": total_reports}


@router.get("/filter")
def get_filter_settings(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """Get user's spam filter settings."""
    f = db.query(SpamFilter).filter(SpamFilter.user_id == current_user.id).first()
    if not f:
        return {"configured": False, "message": "No spam filter configured. Set one up to enable auto-blocking."}
    return {
        "configured": True,
        "is_active": f.is_active,
        "block_unknown_callers": f.block_unknown_callers,
        "block_international": f.block_international,
        "block_voip": f.block_voip,
        "block_premium_rate": f.block_premium_rate,
        "min_spam_score_to_block": f.min_spam_score_to_block,
        "auto_block_reported_spam": f.auto_block_reported_spam,
        "blocked_keywords": f.blocked_keywords,
        "whitelisted_numbers": f.whitelisted_numbers,
    }


@router.post("/filter")
def update_filter(
    body: dict,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """Create or update spam filter settings."""
    f = db.query(SpamFilter).filter(SpamFilter.user_id == current_user.id).first()
    if not f:
        f = SpamFilter(user_id=current_user.id)
        db.add(f)

    for field in [
        "is_active", "block_unknown_callers", "block_international",
        "block_voip", "block_premium_rate", "auto_block_reported_spam",
        "silent_block", "auto_report_blocked",
    ]:
        if field in body:
            setattr(f, field, body[field])

    if "min_spam_score_to_block" in body:
        f.min_spam_score_to_block = max(0.0, min(1.0, body["min_spam_score_to_block"]))
    if "blocked_keywords" in body:
        f.blocked_keywords = body["blocked_keywords"]
    if "whitelisted_numbers" in body:
        f.whitelisted_numbers = body["whitelisted_numbers"]

    db.commit()
    logger.info("SPAM_FILTER_UPDATED user=%d", current_user.id)
    return {"message": "Spam filter updated", "user_id": current_user.id}


@router.get("/history")
def spam_history(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    limit: int = Query(50, ge=1, le=200),
) -> Any:
    """Get spam check history."""
    logs = (
        db.query(SpamLog)
        .filter(SpamLog.user_id == current_user.id)
        .order_by(SpamLog.created_at.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "phone_number": l.phone_number,
            "type": l.spam_type.value if hasattr(l.spam_type, 'value') else l.spam_type,
            "score": l.spam_score,
            "action": l.action_taken.value if hasattr(l.action_taken, 'value') else l.action_taken,
            "reason": l.reason,
            "timestamp": l.created_at.isoformat() if l.created_at else None,
        }
        for l in logs
    ]
