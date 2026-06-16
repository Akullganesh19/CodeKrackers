import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.event_bus import bus
from backend.models.orm import User, Threat
from backend.core.database import AsyncSessionLocal

logger = logging.getLogger("vas.user_intelligence")

async def update_user_intelligence(threat: Threat, user_id: str, **kwargs):
    if not user_id:
        return

    # Extract risk score early before we lose session context if any
    risk_score = threat.risk_score

    try:
        async with AsyncSessionLocal() as session:
            # Retrieve user profile
            result = await session.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()

            if user:
                if user.scams_avoided is None:
                    user.scams_avoided = 0
                user.scams_avoided += 1

                if user.safety_score is None:
                    user.safety_score = 100.0

                if risk_score > 0.8:
                    user.safety_score = min(100.0, user.safety_score + 1.0)
                else:
                    user.safety_score = min(100.0, user.safety_score + 0.5)

                await session.commit()
                logger.info(f"SYNAPSE: Updated intelligence for user {user_id}. Scams avoided: {user.scams_avoided}, Safety Score: {user.safety_score}")
    except Exception as e:
        logger.error(f"Error updating user intelligence: {e}")

# Register listener
bus.on("threat.detected", update_user_intelligence)
