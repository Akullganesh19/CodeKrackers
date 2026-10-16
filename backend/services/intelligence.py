"""
Cross-system intelligence connections.
Synapse Agent.
"""
import logging
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.events import event_bus
from backend.services.audit import log_event, AuditAction
from backend.models.orm import Threat
from backend.models.threat import ThreatStatus

logger = logging.getLogger("vas.synapse")

# Connection: Threats ↔ Audit/Users
# Intelligence: When a threat's status is changed to resolved,
# we should record that the user successfully avoided a scam (scams_avoided++),
# and write an audit log, without coupling the threats endpoint to the users table/audit service directly.

def _update_user_scams_avoided(db: Session, user_id: str):
    from backend.models.orm import User
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.scams_avoided = (user.scams_avoided or 0) + 1
            db.commit()
            logger.info("Synapse: Incremented scams_avoided for user %s", user_id)
    except Exception as e:
        logger.error("Synapse: Failed to update scams_avoided: %s", e)

def on_threat_status_changed(threat_id: str, new_status: str, user_id: str, client_ip: str, db: Session):
    # 1. Audit Log (Threats -> Audit)
    log_event(
        db=db,
        action=AuditAction.THREAT_STATUS_CHANGED,
        ip_address=client_ip,
        user_id=user_id,
        resource_type="threat",
        resource_id=threat_id,
        details={"new_status": new_status},
        severity="info"
    )
    logger.info("Synapse: Recorded THREAT_STATUS_CHANGED audit log for threat %s", threat_id)

    # 2. Intelligence: Update user metrics (Threats -> Users)
    if new_status == ThreatStatus.resolved.value:
        # Find the owner of the threat
        threat = db.query(Threat).filter(Threat.id == threat_id).first()
        if threat and threat.user_id:
            _update_user_scams_avoided(db, threat.user_id)

def setup_intelligence():
    """Wire up the event listeners."""
    event_bus.on("threat.status_changed", on_threat_status_changed)
    logger.info("Synapse: Cross-system intelligence pathways connected.")
