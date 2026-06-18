"""
Threat management endpoints with RBAC, pagination, and status workflow.
"""
import logging
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.api import deps
from backend.core.ws import manager
from backend.models.threat import Threat, ThreatStatus
from backend.models.user import User, UserRole
from backend.schemas.threat import Threat as ThreatSchema
from backend.schemas.threat import ThreatCreate

logger = logging.getLogger("vas.threats")
router = APIRouter()


@router.get("/", response_model=List[ThreatSchema])
def read_threats(
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    threat_type: str = Query(None, description="Filter by type: smishing, vishing, crypto_scam"),
    severity: str = Query(None, description="Filter by severity: low, medium, high, critical"),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """Retrieve threats with filtering and pagination."""
    query = db.query(Threat)

    # RBAC: regular users see only their threats
    if current_user.role not in {UserRole.ADMIN, UserRole.OFFICER, UserRole.SUPER_ADMIN}:
        query = query.filter(Threat.owner_id == current_user.id)

    if threat_type:
        query = query.filter(Threat.type == threat_type)
    if severity:
        query = query.filter(Threat.severity == severity)

    return query.order_by(Threat.timestamp.desc()).offset(skip).limit(limit).all()


@router.post("/", response_model=ThreatSchema, status_code=status.HTTP_201_CREATED)
async def create_threat(
    *,
    db: Session = Depends(deps.get_db),
    threat_in: ThreatCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """Create new threat detection log and broadcast via WebSocket."""
    threat = Threat(
        **threat_in.model_dump(),
        owner_id=current_user.id,
    )
    db.add(threat)
    db.commit()
    db.refresh(threat)

    logger.warning(
        "THREAT_CREATED id=%d type=%s severity=%s source=%s user=%d",
        threat.id, threat.type, threat.severity, threat.source_number, current_user.id,
    )

    # Broadcast to all connected dashboard clients
    await manager.broadcast({
        "type": "NEW_THREAT",
        "data": {
            "id": threat.id,
            "type": threat.type,
            "source": threat.source_number,
            "severity": threat.severity,
            "confidence": threat.confidence_score,
            "timestamp": threat.timestamp.isoformat() if threat.timestamp else None,
        },
    })

    return threat


@router.patch("/{threat_id}/status")
def update_threat_status(
    threat_id: int,
    body: dict,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_officer_or_admin),
) -> Any:
    """Update threat status (officers/admins only)."""
    threat = db.query(Threat).filter(Threat.id == threat_id).first()
    if not threat:
        raise HTTPException(status_code=404, detail="Threat not found")

    new_status = body.get("status")
    try:
        threat.status = ThreatStatus(new_status)
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid status. Must be one of: {[s.value for s in ThreatStatus]}",
        )

    db.commit()
    logger.info("THREAT_STATUS_UPDATED id=%d status=%s by=%d", threat_id, new_status, current_user.id)
    return {"id": threat_id, "status": threat.status}


@router.get("/count")
def threat_count(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """Get total threat count."""
    total = db.query(Threat).count()
    return {"total": total, "ws_clients": manager.client_count}
