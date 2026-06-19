"""
Centralized event listeners to connect isolated systems.
"""
import logging
import asyncio
from sqlalchemy.orm import Session
from backend.core.database import SessionLocal
from backend.models.orm import User
from backend.core.events.bus import event_bus

logger = logging.getLogger("vas.events.listeners")

def update_user_safety_score_sync(user_id: str, risk_score: float):
    db: Session = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            # Increase scams avoided
            user.scams_avoided += 1

            # Boost safety score, capping at 100.0
            boost = 1.0 + (risk_score * 4.0)
            user.safety_score = min(100.0, user.safety_score + boost)

            db.commit()
            logger.info(f"User {user_id} avoided a scam! Score boosted by {boost:.2f}. Total avoided: {user.scams_avoided}")
    except Exception as e:
        logger.error(f"Failed to update safety score for user {user_id}: {e}")
        db.rollback()
    finally:
        db.close()

async def update_user_safety_score_on_threat(event_type: str, **kwargs):
    """
    Enrichment Pattern: Connects Threat Detection to User Gamification.
    """
    user_id = kwargs.get("user_id")
    risk_score = kwargs.get("risk_score", 0.0)

    if not user_id:
        return

    await asyncio.to_thread(update_user_safety_score_sync, user_id, risk_score)

def setup_listeners():
    """Register all cross-system event listeners."""
    logger.info("Setting up cross-system event listeners...")

    # Connect Threats -> User Safety Gamification
    event_bus.subscribe("threat.created", update_user_safety_score_on_threat)
