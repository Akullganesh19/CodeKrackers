import logging
from backend.core.events.bus import event_bus
from backend.models.orm import User
from backend.services.audit import log_event
from backend.core.database import AsyncSessionLocal

logger = logging.getLogger("vas.listeners")

async def sync_auth_to_analytics_on_login(payload: dict):
    """
    Synapse Connection: Auth -> Analytics
    When a user logs in, analyze their historical risk or track their session.
    """
    user_id = payload.get("user_id")
    email = payload.get("email")
    ip_address = payload.get("ip_address")

    logger.info(f"SYNAPSE [Auth -> Analytics]: Enriching login for {email}")

    # We could theoretically calculate the user's risk based on the IP address,
    # or emit a custom Audit event for Analytics to ingest.
    # We will log a special forensic event that the analytics engine can parse.

    async with AsyncSessionLocal() as db:
        # In this synchronous compatibility block or using raw async calls
        # We just log it as an enriched event
        try:
             logger.info(f"Cross-system intelligence: User {user_id} logged in from IP {ip_address}")
        except Exception as e:
             logger.error(f"Synapse Enrichment Error: {e}")

def setup_listeners():
    """Register all Synapse EventBus connections."""
    event_bus.on("user.login", sync_auth_to_analytics_on_login)
    logger.info("Synapse EventBus listeners initialized.")
