from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.main import app
from backend.models.orm import Base
from backend.api import deps
import pytest
from unittest.mock import patch

# Setup test DB
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_adversarial.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[deps.get_db_sync] = override_get_db

@pytest.fixture(autouse=True)
def bypass_rate_limiter(monkeypatch):
    from limits.strategies import FixedWindowRateLimiter
    monkeypatch.setattr(FixedWindowRateLimiter, "hit", lambda self, *args, **kwargs: True)

def test_privilege_escalation_register():
    Base.metadata.create_all(bind=engine)
    client = TestClient(app)

    # Attempt to register an admin user
    response = client.post("/api/auth/register", json={
        "email": "hacker@example.com",
        "password": "StrongPassword123!",
        "role": "admin"
    })
    assert response.status_code == 201

    # Login to check role
    login_resp = client.post("/api/auth/login", json={
        "email": "hacker@example.com",
        "password": "StrongPassword123!"
    })
    assert login_resp.status_code == 200
    assert login_resp.json()["user"]["role"] != "admin", "Privilege escalation successful in /register"
    Base.metadata.drop_all(bind=engine)

def test_privilege_escalation_verify_otp():
    Base.metadata.create_all(bind=engine)
    client = TestClient(app)

    # Attempt to verify OTP with admin role (assuming redis offline bypass)
    response = client.post("/api/auth/verify", json={
        "identifier": "hacker_phone@example.com",
        "code": "123456", # Due to the mock bypass, this might pass if Redis is offline
        "role": "admin"
    })
    assert response.status_code == 200
    token = response.json().get("access_token")

    import jwt
    from backend.core.config import settings
    decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    assert decoded.get("role") != "admin", "Privilege escalation successful in /verify"
    Base.metadata.drop_all(bind=engine)
