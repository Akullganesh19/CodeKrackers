import logging

from backend.core.database import SessionLocal
from backend.core.events.bus import bus
from backend.services.audit import AuditAction, log_event

logger = logging.getLogger("vas.events.listeners")


def handle_account_locked(user_id: str, email: str, ip_address: str):
    logger.info(
        "Cross-system intelligence: Auth event received for "
        f"locked account {email}. Writing to Threat Intel / Audit."
    )

    db = SessionLocal()
    try:
        log_event(
            db=db,
            action=AuditAction.ACCOUNT_LOCKED,
            ip_address=ip_address,
            user_id=int(user_id) if user_id and user_id.isdigit() else None,
            user_email=email,
            severity="warning",
            details={"reason": "Max failed login attempts reached"},
        )
    except Exception as e:
        logger.error(f"Failed to process ACCOUNT_LOCKED event: {e}")
    finally:
        db.close()


bus.subscribe("ACCOUNT_LOCKED", handle_account_locked)
