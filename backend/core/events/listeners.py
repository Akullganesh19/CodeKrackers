import logging
from .bus import event_bus
from backend.core.database import AsyncSessionLocal
from sqlalchemy import select
from backend.models.orm import Threat, User

logger = logging.getLogger("vas.events.listeners")

async def on_auth_failure(payload: dict):
    # Cross-System Intelligence: Auth -> Intel/Threats
    # When repeated auth failures occur, we can track this as a potential threat.
    # We could decrease the user's safety score or log a suspicious activity.
    user_id = payload.get("user_id")
    identifier = payload.get("identifier")

    if user_id:
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            if user:
                # Decrease safety score by a tiny fraction per failure
                new_score = max(0.0, user.safety_score - 1.0)
                logger.info(f"Auth failure for {identifier}, decrementing safety score from {user.safety_score} to {new_score}")
                user.safety_score = new_score
                await db.commit()
    else:
         logger.info(f"Auth failure for unknown identifier: {identifier}")


async def on_auth_success(payload: dict):
     # Reward safety score slightly on successful login
     user_id = payload.get("user_id")

     if user_id:
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            if user and user.safety_score < 100.0:
                 # Slowly recover safety score
                 new_score = min(100.0, user.safety_score + 0.5)
                 logger.info(f"Auth success for {user.email}, incrementing safety score from {user.safety_score} to {new_score}")
                 user.safety_score = new_score
                 await db.commit()

def setup_listeners():
    event_bus.subscribe("auth.failure", on_auth_failure)
    event_bus.subscribe("auth.success", on_auth_success)
    logger.info("Event listeners initialized")
