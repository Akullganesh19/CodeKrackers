from backend.core.events.bus import EventBus
from backend.models.orm import BlacklistType
from backend.services.threat_intel import auto_blacklist
from backend.core.database import SessionLocal
import logging

logger = logging.getLogger("vas.events.listeners")


def handle_account_locked(
    user_email: str, failed_attempts: int, ip_address: str = "unknown", **kwargs
):
    """
    Event listener triggered when an account is locked out after MAX_LOGIN_ATTEMPTS.
    Automatically blacklists the email in Threat Intel.
    """
    logger.info(
        f"Cross-system intel: Account locked for {user_email} after {failed_attempts} "
        "attempts. Adding to Threat Intel blacklist."
    )
    db = SessionLocal()
    try:
        # Cross-system intelligence: Auth (lockout) -> Threat Intel (blacklist)
        auto_blacklist(
            db=db,
            identifier=user_email,
            identifier_type=BlacklistType.EMAIL,
            reason=f"Auto-blacklisted due to {failed_attempts} failed attempts "
                   f"from IP: {ip_address}",
            confidence=0.6,
            source="auth_system_event",
        )
    except Exception as e:
        logger.error(f"Failed to auto-blacklist {user_email}: {e}")
    finally:
        db.close()


# Subscribe the listener to the event
EventBus.subscribe("user.account_locked", handle_account_locked)
