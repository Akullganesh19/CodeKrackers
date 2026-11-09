from fastapi.testclient import TestClient
from backend.main import app
import uuid
import pytest

@pytest.mark.skip(reason="Requires a running local Redis and initialized DB")
def test_register_role_standardization(monkeypatch):
    monkeypatch.setattr("backend.api.auth.redis_client", None)

    app.dependency_overrides = {}
    from backend.core.limiter import limiter
    monkeypatch.setattr(limiter, "limit", lambda x: lambda f: f)

    client = TestClient(app)
    unique_email = f"test_{uuid.uuid4()}@example.com"
    response = client.post(
        "/api/auth/register",
        json={
            "email": unique_email,
            "password": "StrongPassword123!",
            "role": "super_admin"
        }
    )
    assert response.status_code == 201

    login_response = client.post(
        "/api/auth/login",
        json={
            "email": unique_email,
            "password": "StrongPassword123!"
        }
    )
    assert login_response.status_code == 200
    user_data = login_response.json()["user"]
    assert user_data["role"] == "citizen"
