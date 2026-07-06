import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import sys
import os

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.main import app
from backend.models.orm import Base, User
from backend.api import deps
import backend.api.auth as auth

# Mock limiter for tests since redis is offline
from slowapi import Limiter
from slowapi.util import get_remote_address
app.state.limiter = Limiter(key_func=get_remote_address, default_limits=[], enabled=False)
auth.limiter.enabled = False

# Use a synchronous engine for test setup
sync_engine = create_engine("sqlite:///./test_vsdp.db", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

def override_get_db_sync():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[deps.get_db_sync] = override_get_db_sync
# Force main app to use our local session instead of async SessionLocal if needed anywhere
# but we just override the exact dependency auth uses which is get_db_sync

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.drop_all(bind=sync_engine)
    Base.metadata.create_all(bind=sync_engine)
    yield
    Base.metadata.drop_all(bind=sync_engine)

client = TestClient(app)

def test_mass_assignment_register():
    response = client.post("/api/auth/register", json={
        "email": "hacker@evil.com",
        "password": "Password123!",
        "role": "super_admin"  # Should be ignored
    })

    assert response.status_code == 201

    db = TestingSessionLocal()
    user = db.query(User).filter(User.email == "hacker@evil.com").first()
    assert user.role.value == "citizen", "Mass assignment vulnerability! Role was escalated."

def test_mass_assignment_otp_verify():
    # Attempt to inject role during OTP verify for a new phone
    auth.redis_client = None  # Force mock logic

    response = client.post("/api/auth/verify", json={
        "identifier": "0000000000",
        "code": "123456",
        "role": "admin" # Used to be allowed
    })

    # It should fail because the code won't match (since we fixed the mock bypass)
    assert response.status_code == 400

def test_phone_number_creation():
    response = client.post("/api/auth/register", json={
        "email": "phone@user.com",
        "password": "Password123!",
        "phone_number": "1234567890"
    })
    assert response.status_code == 201, f"Failed with {response.status_code}: {response.text}"

    db = TestingSessionLocal()
    user = db.query(User).filter(User.phone == "1234567890").first()
    assert user is not None

def test_redis_offline_fallback():
    # Mock redis offline
    auth.redis_client = None
    response = client.post("/api/auth/verify", json={
        "identifier": "test@user.com",
        "code": "000000"
    })
    assert response.status_code == 400
    assert "Invalid or expired" in response.text
