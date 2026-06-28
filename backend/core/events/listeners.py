import logging
from backend.core.events.bus import event_bus
from backend.core.database import SessionLocal
from backend.models.threat import ThreatType, ThreatSeverity
from backend.models.orm import Threat

logger = logging.getLogger("vas.events.listeners")


def handle_account_locked(
    user_id: str, identifier: str, ip_address: str = "unknown", **kwargs
):
    logger.info(
        f"SYNAPSE: Emitting Threat intelligence for locked account: {identifier}"
    )
    try:
        db = SessionLocal()
        threat = Threat(
            user_id=str(user_id),
            type=ThreatType.OTP_FRAUD,
            severity=ThreatSeverity.HIGH,
            status="detected",
            raw_content=f"Account locked out due to excessive failed login attempts. IP: {ip_address}",
            risk_score=0.9,
            confidence=1.0,
            extra_info={
                "identifier": identifier,
                "ip_address": ip_address,
                "source": "auth_system",
            },
        )
        db.add(threat)
        db.commit()
        db.close()
    except Exception as e:
        logger.error(
            f"Failed to create threat for locked account {identifier}: {e}",
            exc_info=True,
        )


event_bus.subscribe("auth.account_locked", handle_account_locked)
