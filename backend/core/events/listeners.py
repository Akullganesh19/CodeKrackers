import logging
from backend.core.events.bus import EventBus
from backend.models.orm import Threat, ThreatType, ThreatSeverity
from backend.core.database import SessionLocal

logger = logging.getLogger("vas.synapse")

def handle_account_locked(data: dict):
    user_id = data.get("user_id")
    identifier = data.get("identifier")

    logger.info(f"Cross-system intelligence: Auth event received for Threat intel. User {user_id} locked.")

    db = SessionLocal()
    try:
        threat = Threat(
            user_id=user_id,
            type=ThreatType.OTHER,
            severity=ThreatSeverity.HIGH,
            status="detected",
            raw_content=f"Multiple failed login attempts for {identifier}. Account temporarily locked.",
            risk_score=0.9,
            confidence=1.0,
            sender_id=identifier,
            is_reported=False
        )
        db.add(threat)
        db.commit()
    except Exception as e:
        logger.error(f"Failed to record threat from account lock: {e}")
    finally:
        db.close()

EventBus.subscribe("account_locked", handle_account_locked)
