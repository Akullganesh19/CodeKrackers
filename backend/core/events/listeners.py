import logging

from backend.core.database import SessionLocal
from backend.core.events.bus import bus
from backend.models.audit import AuditLog
from backend.models.orm import Blacklist, BlacklistType

logger = logging.getLogger("vas.events.listeners")


def handle_account_locked(user_id: int, identifier: str, ip_address: str) -> None:
    """
    Listener for account_locked event.
    Records an AuditLog and adds the IP to Blacklist.
    """
    logger.info(
        f"Cross-system intelligence: account_locked event triggered for user {user_id}"
    )
    with SessionLocal() as db:
        # Log to AuditLog
        try:
            audit = AuditLog(
                user_id=user_id,
                action="ACCOUNT_LOCKED",
                ip_address=ip_address,
                details={"identifier": identifier, "reason": "brute_force_login"},
                severity="warning",
            )
            db.add(audit)
        except Exception as e:
            logger.error(f"Failed to create AuditLog in listener: {e}")

        # Add IP to Blacklist
        try:
            if ip_address and ip_address != "127.0.0.1" and ip_address != "unknown":
                existing = (
                    db.query(Blacklist)
                    .filter(
                        Blacklist.type == BlacklistType.IP,
                        Blacklist.value == ip_address,
                    )
                    .first()
                )
                if existing:
                    existing.report_count += 1
                    existing.confidence = min(existing.confidence + 0.1, 1.0)
                else:
                    blacklist_entry = Blacklist(
                        type=BlacklistType.IP,
                        value=ip_address,
                        reason="Brute force login attempts leading to account lockout",
                        confidence=0.8,
                        source="auth_system",
                        reported_by=user_id,
                    )
                    db.add(blacklist_entry)
        except Exception as e:
            logger.error(f"Failed to add to Blacklist in listener: {e}")

        db.commit()


# Register listeners
bus.subscribe("account_locked", handle_account_locked)
