import logging

from backend.core.database import SessionLocal
from backend.core.events.bus import bus
from backend.models.orm import Threat, ThreatSeverity, ThreatType

logger = logging.getLogger("vas.events.listeners")


def handle_account_locked(
    user_id: str, identifier: str, ip_address: str, attempts: int, source: str
):
    """
    Listens for account lockouts from the Auth system and generates a Threat record
    for the Threat/Analytics system to process.
    """
    logger.info(f"Event received: user.account_locked for {identifier}")
    try:
        # Use sync session because we might be called from a sync route (like login)
        with SessionLocal() as db:
            # Create a threat indicating potential credential stuffing or brute force
            threat = Threat(
                user_id=user_id,
                type=ThreatType.OTHER,
                severity=ThreatSeverity.HIGH,
                raw_content=(
                    "Brute force attempt detected. "
                    f"Account locked after {attempts} failed attempts."
                ),
                risk_score=0.9,
                confidence=1.0,
                caller_id=ip_address,  # Repurposed to store IP
                sender_id=source,
                extra_info={
                    "event_type": "user.account_locked",
                    "identifier": identifier,
                    "ip_address": ip_address,
                    "failed_attempts": attempts,
                    "source": source,
                },
            )
            db.add(threat)
            db.commit()
            logger.info(
                f"Successfully generated Threat from account lock for {identifier}"
            )
    except Exception as e:
        logger.error(f"Failed to process account locked event: {e}", exc_info=True)


# Register listeners
bus.subscribe("user.account_locked", handle_account_locked)
