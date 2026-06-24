import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.models.orm import Base, User
from datetime import datetime, timezone
import uuid

@pytest.fixture(scope="module")
def engine():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    yield engine
    engine.dispose()

@pytest.fixture
def db_session(engine):
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    yield session
    session.close()

def test_user_failed_login_attempts(db_session):
    u = User(id=str(uuid.uuid4()), email="test1@test.com", hashed_password="pw")
    db_session.add(u)
    db_session.commit()
    db_session.refresh(u)

    assert u.failed_login_attempts == 0
    assert u.locked_until is None

    u.failed_login_attempts = 5
    u.locked_until = datetime.now(timezone.utc)
    u.last_login_at = datetime.now(timezone.utc)
    db_session.commit()

    db_session.expunge_all()
    u_loaded = db_session.query(User).filter(User.email == "test1@test.com").first()

    assert u_loaded.failed_login_attempts == 5
    assert u_loaded.locked_until is not None
    assert u_loaded.last_login_at is not None
