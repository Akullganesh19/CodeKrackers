import time
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.models.orm import UserConsent, User, Base

engine = create_engine('sqlite:///:memory:')
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def setup_data(db, count=1000):
    user = db.query(User).filter_by(id=1).first()
    if not user:
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
            consent_user_agent="benchmark"
        )
        for _ in range(count)
    ]
    db.bulk_save_objects(consents)
    db.commit()

def run_unoptimized(db):
    start = time.perf_counter()
    consents = (
        db.query(UserConsent)
        .filter(UserConsent.user_id == 1, UserConsent.is_revoked == False)
        .all()
    )
    for c in consents:
        c.is_revoked = True
        c.revoked_at = datetime.now(timezone.utc)
    db.commit()
    end = time.perf_counter()
    return end - start

def run_optimized(db):
    start = time.perf_counter()
    db.query(UserConsent).filter(UserConsent.user_id == 1, UserConsent.is_revoked == False).update(
        {"is_revoked": True, "revoked_at": datetime.now(timezone.utc)},
        synchronize_session=False
    )
    db.commit()
    end = time.perf_counter()
    return end - start

if __name__ == "__main__":
    db = SessionLocal()

    # Test Unoptimized
    setup_data(db, 1000)
    unoptimized_time = run_unoptimized(db)
    print(f"Unoptimized time (1000 records): {unoptimized_time:.4f} seconds")

    # Clean DB
    db.query(UserConsent).delete()
    db.commit()

    # Test Optimized
    setup_data(db, 1000)
    optimized_time = run_optimized(db)
    print(f"Optimized time (1000 records): {optimized_time:.4f} seconds")

    print(f"Improvement: {unoptimized_time / optimized_time:.2f}x faster")
