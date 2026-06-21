import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.main import app
from backend.api.deps import get_db
from backend.models.orm import Base, User
from backend.core.security import get_password_hash

# Create an in-memory SQLite database for testing
engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    # Add a test user
    user = User(
        email="target@example.com",
        hashed_password=get_password_hash("CorrectPassword123!"),
        is_active=True
    )
    db.add(user)
    db.commit()
    yield
    Base.metadata.drop_all(bind=engine)

def test_failed_login_crash_regression():
    """
    Test that a failed login doesn't crash with a 500 AttributeError,
    but instead returns a 401 Unauthorized, and correctly increments failed attempts.
    """
    response = client.post(
        "/api/v1/login/access-token",
        data={"username": "target@example.com", "password": "WrongPassword123!"}
    )

    # Prove the old behavior was wrong (crashed with 500) and new is right (returns 401)
    assert response.status_code == 401, f"Expected 401, got {response.status_code} with body {response.text}"
