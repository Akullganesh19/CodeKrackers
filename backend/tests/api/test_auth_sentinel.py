import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.main import app
from backend.api import deps
from backend.models.orm import Base, User, UserRole
from backend.core.security import get_password_hash








from unittest.mock import patch, MagicMock

@pytest.fixture(autouse=True)
def mock_redis_client():
    with patch('backend.core.limiter.limiter.limit', lambda *args, **kwargs: lambda f: f), \
         patch('backend.api.auth.limiter.limit', lambda *args, **kwargs: lambda f: f), \
         patch('slowapi.extension.Limiter.limit', lambda self, *args, **kwargs: lambda f: f), \
         patch('backend.api.auth.redis_client') as mock_redis:
        mock_redis.get.return_value = "123456" # for otp verify

        # Also mock get_password_hash since it's breaking on bcrypt truncate
        with patch('backend.core.security.get_password_hash', return_value="dummy_hash"):
            yield mock_redis

# Setup test DB
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_sentinel.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db_sync():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[deps.get_db_sync] = override_get_db_sync
client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_mass_assignment_register():
    response = client.post("/api/auth/register", json={
        "email": "hacker@example.com",
        "password": "StrongPassword123!",
        "role": "super_admin"
    })
    assert response.status_code == 201

    # Check what role was actually assigned
    db = TestingSessionLocal()
    user = db.query(User).filter(User.email == "hacker@example.com").first()
    assert user.role == UserRole.CITIZEN, f"Vulnerability! User got role: {user.role}"
    db.close()

def test_mass_assignment_verify_otp():
    # Attempt to verify OTP with a new user but inject admin role
    response = client.post("/api/auth/verify", json={
        "identifier": "hacker_phone@example.com",
        "code": "123456",
        "role": "admin"
    })
    assert response.status_code == 200

    db = TestingSessionLocal()
    user = db.query(User).filter(User.email == "hacker_phone@example.com").first()
    assert user.role == UserRole.CITIZEN, f"Vulnerability! User got role: {user.role}"
    db.close()
