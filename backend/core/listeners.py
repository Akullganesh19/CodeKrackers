import logging
from backend.core.event_bus import event_bus
from backend.core.database import SessionLocal
from backend.models.orm import User

logger = logging.getLogger("vas.listeners")

def handle_spam_reported(user_id: int):
    """
    Event listener for 'spam.reported'.
    Increments the user's scams_avoided counter and rewards them with safety score points.
    """
    try:
        db = SessionLocal()
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.scams_avoided += 1
            # Reward for proactively reporting spam
            user.safety_score = min(100.0, user.safety_score + 1.0)
            db.commit()
            logger.info(f"User {user_id} rewarded for reporting spam. New score: {user.safety_score}, avoided: {user.scams_avoided}")
    except Exception as e:
        logger.error(f"Error handling spam.reported event for user {user_id}: {e}")
    finally:
        db.close()

def setup_listeners():
    """Register all application event listeners."""
    event_bus.subscribe("spam.reported", handle_spam_reported)
    logger.info("Event listeners registered.")
