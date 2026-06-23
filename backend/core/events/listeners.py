import logging
from backend.core.events.bus import bus
from backend.models.orm import Threat, ThreatType, ThreatSeverity
from backend.core.database import AsyncSessionLocal

logger = logging.getLogger("vas.events.listeners")

async def log_failed_login_as_threat(user_email: str, ip_address: str = "Unknown"):
    """
    Listener that converts repeated failed login attempts into a logged Threat.
    Intelligence created: Security system now knows about Auth brute force attempts.
    """
    logger.info(f"Analyzing failed login for {user_email}")
    async with AsyncSessionLocal() as db:
        threat = Threat(
            type=ThreatType.OTP_FRAUD,  # Best match for auth fraud
            severity=ThreatSeverity.MEDIUM,
            raw_content=f"Suspicious login activity detected for {user_email} from IP {ip_address}",
            risk_score=0.6,
            confidence=0.8,
            extra_info={"user_email": user_email, "ip": ip_address, "source": "auth_system"}
        )
        db.add(threat)
        await db.commit()
        logger.warning(f"Auth-to-Threat correlation created for {user_email}")

def setup_listeners():
    """Register all cross-system intelligence pathways."""
    bus.subscribe("auth.failed_login_limit_reached", log_failed_login_as_threat)
    logger.info("EventBus listeners initialized")
