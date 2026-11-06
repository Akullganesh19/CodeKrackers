"""
Blacklist management and threat intelligence endpoints.
"""
from backend.core.logger import get_logger
import logging
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.api import deps
from backend.models.orm import Blacklist as BlacklistEntry, BlacklistType, User, UserRole
from backend.services.threat_intel import auto_blacklist, calculate_threat_score

logger = get_logger("vas.blacklist")
router = APIRouter()


@router.post("/report")
def report_scammer(
    body: dict,
    db: Session = Depends(deps.get_db_sync),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """Report a phone number, domain, IP, or wallet as scam."""
    identifier = body.get("identifier", "").strip()
    id_type = body.get("type", "phone")
    reason = body.get("reason", "User report")

    if not identifier:
        raise HTTPException(status_code=422, detail="identifier is required")

    try:
        bl_type = BlacklistType(id_type)
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid type. Must be one of: {[t.value for t in BlacklistType]}",
        )

    entry = auto_blacklist(
        db=db,
        identifier=identifier,
        identifier_type=bl_type,
        reason=reason,
        reported_by=current_user.id,
        confidence=0.5,
        source="user_report",
    )

    logger.info("SCAMMER_REPORTED by=%d type=%s value=%s", current_user.id, id_type, identifier)
    return {
        "id": entry.id,
        "type": entry.type,
        "value": entry.value,
        "confidence": entry.confidence,
        "report_count": entry.report_count,
    }


@router.get("/lookup")
def lookup_identifier(
    identifier: str = Query(..., min_length=1),
    db: Session = Depends(deps.get_db_sync),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """Check if a phone/domain/IP/wallet is blacklisted."""
    entry = db.query(BlacklistEntry).filter(BlacklistEntry.value == identifier).first()
    if not entry:
        return {"found": False, "identifier": identifier}

    return {
        "found": True,
        "identifier": identifier,
        "type": entry.type,
        "confidence": entry.confidence,
        "report_count": entry.report_count,
        "is_verified": entry.is_verified,
        "source": entry.source,
    }


@router.get("/list")
def list_blacklist(
    db: Session = Depends(deps.get_db_sync),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    bl_type: str = Query(None),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """List blacklisted entries (officers/admins see all, users see verified only)."""
    query = db.query(BlacklistEntry)

    if bl_type:
        query = query.filter(BlacklistEntry.type == bl_type)

    if current_user.role not in {UserRole.ADMIN, UserRole.OFFICER, UserRole.SUPER_ADMIN}:
        query = query.filter(BlacklistEntry.is_verified == True)

    entries = query.order_by(BlacklistEntry.confidence.desc()).offset(skip).limit(limit).all()
    return [
        {
            "id": e.id,
            "type": e.type,
            "value": e.value,
            "confidence": e.confidence,
            "report_count": e.report_count,
            "is_verified": e.is_verified,
            "source": e.source,
        }
        for e in entries
    ]


@router.post("/scan")
def scan_content(
    body: dict,
    db: Session = Depends(deps.get_db_sync),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """Run the multi-engine threat intelligence scan on arbitrary content."""
    content = body.get("content", "")
    sender = body.get("sender", "")

    if not content:
        raise HTTPException(status_code=422, detail="content is required")

    result = calculate_threat_score(content, sender, db)
    return result
