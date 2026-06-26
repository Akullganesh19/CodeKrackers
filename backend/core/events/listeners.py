import logging
from backend.core.events.bus import bus
from backend.core.database import SessionLocal
from backend.models.orm import Blacklist as BlacklistEntry, BlacklistType
from backend.services.threat_intel import auto_blacklist

logger = logging.getLogger("vas.events.listeners")

def handle_account_locked(email: str, ip_address: str, **kwargs) -> None:
    """
    Listener for when an account gets locked due to brute-force attempts.
    Automatically adds the attacker's IP to the Blacklist table.
    Must be synchronous because it is triggered from worker threads.
    """
    logger.info(f"Event received: ACCOUNT_LOCKED for email={email}, ip={ip_address}")

    if not ip_address or ip_address == "unknown":
        logger.debug("Cannot blacklist unknown IP address.")
        return

    db = SessionLocal()
    try:
        auto_blacklist(
            db=db,
            identifier=ip_address,
            identifier_type=BlacklistType.IP,
            reason=f"Automated blacklist: Brute-force attack detected on account {email}",
            reported_by=None,  # System generated
            confidence=0.8,
            source="system_auth_lockout"
        )
        logger.info(f"Successfully auto-blacklisted IP {ip_address}")
    except Exception as e:
        logger.error(f"Failed to auto-blacklist IP {ip_address}: {e}", exc_info=True)
    finally:
        db.close()

def setup_listeners():
    """
    Register all cross-system event listeners.
    Call this function during application startup.
    """
    bus.on("ACCOUNT_LOCKED", handle_account_locked)
    logger.info("Event listeners setup complete.")
