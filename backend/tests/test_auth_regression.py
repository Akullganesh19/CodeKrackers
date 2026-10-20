import pytest
from fastapi.testclient import TestClient

# Mock the entire application starting point since there are too many external module dependencies (whisper, groq, aiosqlite, pydantic_settings, etc) missing in the default venv
import sys
from unittest.mock import MagicMock

# Create a mock for missing module whisper
sys.modules['whisper'] = MagicMock()
sys.modules['ffmpeg'] = MagicMock()
sys.modules['numpy'] = MagicMock()
sys.modules['pandas'] = MagicMock()
sys.modules['sentence_transformers'] = MagicMock()
sys.modules['faiss'] = MagicMock()
sys.modules['nltk'] = MagicMock()
sys.modules['bs4'] = MagicMock()

try:
    from backend.main import app
    client = TestClient(app)
except Exception as e:
    pytest.skip(f"Could not import app: {e}", allow_module_level=True)

def test_register_privilege_escalation():
    # Attempt to register as an admin
    response = client.post("/api/auth/register", json={
        "email": "hacker2@evil.com",
        "password": "Password123!",
        "role": "admin"
    })
    assert response.status_code == 201

    # Login to verify the actual role assigned
    login_response = client.post("/api/auth/login", json={
        "username": "hacker2@evil.com",
        "password": "Password123!",
        "role": "admin"
    })
    # The login should fail or indicate unauthorized because the role is citizen, not admin
    assert login_response.status_code == 401

    # Login as citizen should work
    login_response_citizen = client.post("/api/auth/login", json={
        "username": "hacker2@evil.com",
        "password": "Password123!",
        "role": "citizen"
    })
    assert login_response_citizen.status_code == 200
    data = login_response_citizen.json()
    assert data["user"]["role"] == "citizen"
