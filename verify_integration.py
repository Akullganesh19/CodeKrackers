from backend.core.database import SessionLocal
from backend.services.spam_shield import check_spam
from backend.models import User, SpamType
import uuid

db = SessionLocal()

# Find an existing user or create mock
user = db.query(User).first()
if not user:
    # create a mock one
    user = User(
        id=str(uuid.uuid4()),
        email="mock@test.com",
        phone="1234567890",
        hashed_password="mock",
        safety_score=60.0
    )
    db.add(user)
    db.commit()

original_score = user.safety_score
user.safety_score = 60.0
db.commit()

try:
    res = check_spam(db, "1234567890", str(user.id), SpamType.SMS, "urgent click link here")
    print(res["breakdown"])
except Exception as e:
    print(f"Error checking spam: {e}")

user.safety_score = original_score
db.commit()
db.close()
