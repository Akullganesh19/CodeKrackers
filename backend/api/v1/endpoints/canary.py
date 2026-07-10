"""
Canary Token Tracking Endpoints.

These endpoints handle:
  1. /canary/track/{token} - Tracking URL that triggers when accessed
  2. /canary/status - Check status of planted canaries (admin only)
  3. /canary/plant - Manually plant a new canary (admin only)

The tracking URLs are embedded inside fake database records. When an attacker
exfiltrates data and then accesses the tracking URL, we get an immediate alert.
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from backend.api import deps
from backend.db.session import get_db
from backend.models.canary import CanaryToken
from backend.models.user import User
from backend.services import canary_service

logger = logging.getLogger("vas.canary")
router = APIRouter()


@router.get("/track/{token}")
async def track_canary(
    token: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Tracking URL embedded in fake database records.

    When an attacker accesses this URL (e.g., by clicking a link in
    exfiltrated data), we capture their IP, User-Agent, and timestamp.

    Returns a 1x1 transparent GIF to avoid detection.
    """
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "") or "unknown"

    canary = canary_service.trigger_canary(
        db,
        token=token,
        ip=client_ip,
        user_agent=user_agent,
        path=str(request.url.path),
    )

    if canary:
        logger.critical(
            "CANARY TRACKING URL ACCESSED! token=%s ip=%s ua=%s planted_in=%s",
            token[:16],
            client_ip,
            user_agent[:80],
            canary.planted_in,
        )

    # Return a 1x1 transparent GIF to avoid detection
    # This makes the tracking request look like a broken image or tracking pixel
    gif_data = (
        b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00"
        b"\x00\xff\xff\xff\x00\x00\x00\x21\xf9\x04\x00\x00"
        b"\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00"
        b"\x00\x02\x02\x44\x01\x00\x3b"
    )
    return JSONResponse(
        content=None,
        headers={
            "Content-Type": "image/gif",
            "Cache-Control": "no-store, no-cache, must-revalidate",
            "Pragma": "no-cache",
            "X-Canary": "tracked",
        },
    )


@router.get("/status")
def canary_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
):
    """Get status of all planted canary tokens."""
    tokens = db.query(CanaryToken).all()
    total = len(tokens)
    triggered = sum(1 for t in tokens if t.accessed)
    untriggered = total - triggered

    return {
        "total_tokens": total,
        "triggered": triggered,
        "untriggered": untriggered,
        "tokens": [
            {
                "id": t.id,
                "type": t.token_type,
                "planted_in": t.planted_in,
                "description": t.description,
                "accessed": t.accessed,
                "accessed_at": t.accessed_at,
                "access_ip": t.access_ip,
                "access_count": t.access_count,
            }
            for t in tokens
        ],
    }


@router.post("/plant")
def plant_canary(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
    token_type: str = Query("custom", description="Type of canary token"),
    description: Optional[str] = Query(None, description="Description"),
    planted_in: Optional[str] = Query(None, description="Where this is planted"),
):
    """Manually plant a new canary token."""
    canary = canary_service.create_canary_token(
        db,
        token_type=token_type,
        description=description or f"Manually planted by {current_user.email}",
        planted_in=planted_in or "manual",
    )
    return {
        "message": "Canary token planted",
        "token_id": canary.id,
        "token_type": canary.token_type,
        "planted_in": canary.planted_in,
        "created_at": canary.created_at,
    }


@router.post("/seed")
def seed_canaries(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
):
    """Plant the full set of initial canary tokens."""
    canary_service.plant_seed_tokens(db)
    count = db.query(CanaryToken).count()
    return {
        "message": f"Database seeded with {count} canary tokens",
        "total_tokens": count,
    }
