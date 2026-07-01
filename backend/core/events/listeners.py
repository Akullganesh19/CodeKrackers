import logging
from typing import Any

from backend.core.events.bus import EventBus
from backend.core.database import SessionLocal
from backend.models.orm import Threat, ThreatType, ThreatSeverity
from backend.core.logger import get_logger

logger = get_logger("vas.events.listeners")


@EventBus.on("account_locked")
def handle_account_locked(user_id: str, email: str, ip_address: str, **kwargs: Any):
    """
    Cross-system intelligence: Auth ↔ Threats
    When an account is locked due to brute force, automatically register a Threat.
    """
    logger.info("Event 'account_locked' received for email=%s, ip=%s", email, ip_address)
    db = SessionLocal()
    try:
        # Create a threat entity for the brute force attack
        threat = Threat(
            user_id=user_id,
            type=ThreatType.OTHER,
            severity=ThreatSeverity.HIGH,
            status="detected",
            raw_content=f"Brute force login attack detected for email {email} from IP {ip_address}. Account has been locked.",
            risk_score=90.0,
            confidence=100.0,
            extra_info={"email": email, "ip_address": ip_address, "event": "account_locked_brute_force"}
        )
        db.add(threat)
        db.commit()
        logger.info("Threat entity created for locked account email=%s", email)
    except Exception as e:
        db.rollback()
        logger.error("Failed to create threat for locked account email=%s: %s", email, e, exc_info=True)
    finally:
        db.close()
