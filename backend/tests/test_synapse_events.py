import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.core.events.bus import EventBus
from backend.models.orm import Base, Threat, ThreatType, ThreatSeverity


@pytest.fixture
def db_session():
    # Setup in-memory sqlite for tests
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()

    # We have to patch backend.core.events.listeners.SessionLocal
    import backend.core.events.listeners as listeners

    original_session_local = listeners.SessionLocal
    listeners.SessionLocal = TestingSessionLocal

    yield db
    db.close()
    listeners.SessionLocal = original_session_local
    Base.metadata.drop_all(bind=engine)


def test_auth_lockout_generates_threat(db_session):
    import backend.core.events.listeners  # noqa: F401

    test_user_id = "test-user-uuid"
    test_identifier = "test@example.com"

    # Simulate the event that Auth would emit
    EventBus.publish(
        "account_locked", {"user_id": test_user_id, "identifier": test_identifier}
    )

    # Check if Threat intelligence system caught it
    threats = db_session.query(Threat).filter(Threat.user_id == test_user_id).all()

    assert len(threats) == 1
    threat = threats[0]

    assert threat.type == ThreatType.OTHER
    assert threat.severity == ThreatSeverity.HIGH
    assert test_identifier in threat.raw_content
    assert threat.status == "detected"
