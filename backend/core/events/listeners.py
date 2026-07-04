import logging
from backend.core.event_bus import event_bus
from backend.core.database import AsyncSessionLocal
from backend.models.threat import ThreatType, ThreatSeverity
from backend.models.orm import Threat

logger = logging.getLogger("vas.events.listeners")

async def handle_account_locked(user_id: str, identifier: str, attempt_count: int, **kwargs):
    """
    Listens for account lockout events and automatically registers a Threat,
    effectively linking the Auth system's data with Threat Intelligence.
    """
    try:
        logger.info(f"Cross-system sync: Auth reported lockout for {identifier}. Creating Threat Intel record.")

        async with AsyncSessionLocal() as db:
            threat = Threat(
                user_id=user_id,
                type=ThreatType.other,
                severity=ThreatSeverity.high,
                risk_score=0.9,
                confidence=1.0,
                sender_id=identifier,
                raw_content=f"System blocked account due to {attempt_count} failed login attempts. Potential account takeover or brute-force attack.",
                extra_info={"source": "auth_system", "action": "account_locked", "failed_attempts": attempt_count}
            )

            db.add(threat)
            await db.commit()
            logger.info(f"Successfully recorded Threat for locked account {identifier}.")

    except Exception as e:
        # Prevent secondary failures from crashing the primary Auth flow
        logger.error(f"Failed to create Threat for locked account {identifier}: {e}", exc_info=True)

# Register the listener with the EventBus
event_bus.subscribe("account_locked", handle_account_locked)
