import logging
from backend.core.events.bus import event_bus
from backend.core.database import SessionLocal
from backend.models.orm import Threat, ThreatType, ThreatSeverity
import json

logger = logging.getLogger("vas.events.listeners")

def on_user_locked(data: dict) -> None:
    """
    Cross-system intelligence listener: Auth -> Analytics/Threats.
    When an account is locked due to brute force, surface it as a Threat.
    """
    logger.info(f"Intelligence Bridge: Processing user.locked event for {data.get('email')}")
    db = SessionLocal()
    try:
        user_id = data.get("user_id")
        email = data.get("email")
        ip_address = data.get("ip_address")

        # Create a threat record for account takeover attempt
        threat = Threat(
            user_id=user_id,
            type=ThreatType.OTHER,
            severity=ThreatSeverity.HIGH,
            status="detected",
            raw_content=f"Account takeover / brute force attempt on {email} from IP {ip_address}",
            risk_score=90.0,
            confidence=0.9,
            sender_id=ip_address,
            extra_info=json.dumps({"source_system": "auth", "event": "account_locked", "ip_address": ip_address})
        )
        db.add(threat)
        db.commit()
        logger.info(f"Generated threat record for locked account {email}")
    except Exception as e:
        logger.error(f"Error in on_user_locked event handler: {e}")
        db.rollback()
    finally:
        db.close()

def setup_listeners() -> None:
    """Initialize all cross-system event listeners."""
    logger.info("Setting up EventBus listeners...")
    event_bus.subscribe("user.locked", on_user_locked)
