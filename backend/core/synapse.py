from backend.core.events import event_bus
from backend.models.orm import User, Threat, ThreatType, ThreatSeverity
from backend.core.database import AsyncSessionLocal
import logging
import asyncio

logger = logging.getLogger("vas.synapse")

# Need to run async db actions from potentially sync/async contexts safely.
def run_async_in_background(coro):
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(coro)
    except RuntimeError:
        asyncio.run(coro)

async def _increment_scams_avoided(user_id):
    async with AsyncSessionLocal() as db:
        user = await db.get(User, user_id)
        if user:
            user.scams_avoided = (user.scams_avoided or 0) + 1
            await db.commit()
            logger.info(f"SYNAPSE: Incremented scams_avoided for user {user_id}")

def handle_threat_blocked(payload):
    """Updates user's scams_avoided counter when SpamShield blocks a threat."""
    user_id = payload.get("user_id")
    if not user_id:
        return
    run_async_in_background(_increment_scams_avoided(user_id))

async def _create_threat_log(user_id):
    async with AsyncSessionLocal() as db:
        threat = Threat(
            user_id=str(user_id),
            type=ThreatType.OTHER,
            severity=ThreatSeverity.HIGH,
            status="detected",
            raw_content="Account locked due to multiple failed login attempts.",
            risk_score=0.9,
            confidence=1.0,
            extra_info={"source": "auth_system", "event": "account_locked"}
        )
        db.add(threat)
        await db.commit()
        logger.info(f"SYNAPSE: Created Threat for locked account of user {user_id}")

def handle_account_locked(payload):
    """Creates a Threat log when Auth locks an account due to brute force."""
    user_id = payload.get("user_id")
    if not user_id:
        return
    run_async_in_background(_create_threat_log(user_id))

def setup_synapse_connections():
    event_bus.subscribe("threat.blocked", handle_threat_blocked)
    event_bus.subscribe("auth.account_locked", handle_account_locked)
    logger.info("🧠 Synapse pathways initialized.")
