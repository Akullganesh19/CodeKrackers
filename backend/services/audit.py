"""
Audit service for persistent forensic event logging.
"""
import logging
from typing import Optional

from sqlalchemy.orm import Session

from backend.models.audit import AuditLog

logger = logging.getLogger("vas.audit")


def log_event(
    db: Session,
    action: str,
    ip_address: str,
    user_id: Optional[int] = None,
    user_email: Optional[str] = None,
    user_agent: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_id: Optional[int] = None,
    details: Optional[dict] = None,
    severity: str = "info",
) -> None:
    """Write an audit event to the database."""
    try:
        entry = AuditLog(
            user_id=user_id,
            user_email=user_email,
            ip_address=ip_address,
            user_agent=(user_agent or "")[:512],
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            severity=severity,
        )
        db.add(entry)
        db.commit()
    except Exception as e:
        logger.error("Failed to write audit log: %s", e)
        db.rollback()


# ─── Common audit actions ───
class AuditAction:
    LOGIN_SUCCESS = "LOGIN_SUCCESS"
    LOGIN_FAILED = "LOGIN_FAILED"
    ACCOUNT_LOCKED = "ACCOUNT_LOCKED"
    USER_CREATED = "USER_CREATED"
    PASSWORD_CHANGED = "PASSWORD_CHANGED"
    THREAT_CREATED = "THREAT_CREATED"
    THREAT_STATUS_CHANGED = "THREAT_STATUS_CHANGED"
    FIR_GENERATED = "FIR_GENERATED"
    FIR_STATUS_CHANGED = "FIR_STATUS_CHANGED"
    BLACKLIST_ADDED = "BLACKLIST_ADDED"
    WAF_BLOCKED = "WAF_BLOCKED"
    EXPORT_DATA = "EXPORT_DATA"
