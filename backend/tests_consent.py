import pytest
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.models.orm import UserConsent, User, Base

engine = create_engine('sqlite:///:memory:')
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def test_consent():
    db = SessionLocal()
    user = User(id=1, email="test@test.com", hashed_password="pw", is_active=True)
    db.add(user)
    db.commit()

    consents = [
        UserConsent(
            user_id=1,
            is_revoked=False,
            consent_phone_lookup=True,
            consent_device_info=True,
            consent_ip="127.0.0.1",
            consent_user_agent="test"
        )
        for _ in range(3)
    ]
    db.bulk_save_objects(consents)
    db.commit()

    # Simulate grant_consent
    db.query(UserConsent).filter(
        UserConsent.user_id == 1, UserConsent.is_revoked == False
    ).update(
        {"is_revoked": True, "revoked_at": datetime.now(timezone.utc)},
        synchronize_session=False,
    )
    db.commit()

    # Check
    revoked = db.query(UserConsent).filter_by(is_revoked=True).count()
    assert revoked == 3

if __name__ == "__main__":
    test_consent()
    print("Test passed.")
