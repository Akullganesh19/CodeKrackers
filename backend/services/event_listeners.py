import logging
from backend.core.events import event_bus
from backend.services.audit import log_event, AuditAction

logger = logging.getLogger("vas.event_listeners")

def handle_login_success(**kwargs):
    logger.info("Handling auth.login_success event (Cross-system data flow from Auth to Audit)")
    db = kwargs.get("db")
    if db:
        log_event(
            db=db,
            action=AuditAction.LOGIN_SUCCESS,
            ip_address=kwargs.get("ip_address"),
            user_id=kwargs.get("user_id"),
            user_email=kwargs.get("user_email"),
            user_agent=kwargs.get("user_agent"),
        )

def handle_login_failed(**kwargs):
    logger.info("Handling auth.login_failed event (Cross-system data flow from Auth to Audit)")
    db = kwargs.get("db")
    if db:
        log_event(
            db=db,
            action=AuditAction.LOGIN_FAILED,
            ip_address=kwargs.get("ip_address"),
            user_email=kwargs.get("user_email"),
            user_agent=kwargs.get("user_agent"),
        )

def handle_account_locked(**kwargs):
    logger.info("Handling auth.account_locked event (Cross-system data flow from Auth to Audit)")
    db = kwargs.get("db")
    if db:
        log_event(
            db=db,
            action=AuditAction.ACCOUNT_LOCKED,
            ip_address=kwargs.get("ip_address"),
            user_id=kwargs.get("user_id"),
            user_email=kwargs.get("user_email"),
            user_agent=kwargs.get("user_agent"),
        )

# Register listeners
event_bus.on("auth.login_success", handle_login_success)
event_bus.on("auth.login_failed", handle_login_failed)
event_bus.on("auth.account_locked", handle_account_locked)
