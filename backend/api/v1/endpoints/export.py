"""
Data export endpoints for reports, evidence, and compliance.
"""

import csv
import io
import logging
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from backend.api import deps
from backend.models.threat import Threat
from backend.models.user import User

logger = logging.getLogger("vas.export")
router = APIRouter()


@router.get("/threats/csv")
def export_threats_csv(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_admin),
    limit: int = Query(500, ge=1, le=5000),
) -> Any:
    """Export threat data as CSV (admin only)."""
    threats = db.query(Threat).order_by(Threat.detected_at.desc()).limit(limit).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "ID",
            "Type",
            "Source",
            "Severity",
            "Confidence",
            "Status",
            "Timestamp",
            "Content",
        ]
    )

    for t in threats:
        writer.writerow(
            [
                t.id,
                t.type.value if hasattr(t.type, "value") else t.type,
                t.sender_id,
                t.severity.value if hasattr(t.severity, "value") else t.severity,
                t.confidence,
                (
                    t.status.value
                    if hasattr(t.status, "value")
                    else getattr(t, "status", "detected")
                ),
                t.detected_at.isoformat() if t.detected_at else "",
                (t.raw_content or "")[:200],
            ]
        )

    output.seek(0)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"vas_threats_export_{timestamp}.csv"

    logger.info("EXPORT_CSV user=%d count=%d", current_user.id, len(threats))

    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/threats/json")
def export_threats_json(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_admin),
    limit: int = Query(500, ge=1, le=5000),
) -> Any:
    """Export threat data as JSON (admin only)."""
    threats = db.query(Threat).order_by(Threat.detected_at.desc()).limit(limit).all()

    data = [
        {
            "id": t.id,
            "type": t.type.value if hasattr(t.type, "value") else t.type,
            "sender_id": t.sender_id,
            "severity": (
                t.severity.value if hasattr(t.severity, "value") else t.severity
            ),
            "confidence": t.confidence,
            "timestamp": t.detected_at.isoformat() if t.detected_at else None,
            "raw_content": t.raw_content,
            "extra_info": t.extra_info,
        }
        for t in threats
    ]

    logger.info("EXPORT_JSON user=%d count=%d", current_user.id, len(threats))
    return {
        "export_time": datetime.now(timezone.utc).isoformat(),
        "count": len(data),
        "threats": data,
    }
