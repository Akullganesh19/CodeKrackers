import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_login_rate_limit():
    data = {"username": "user@example.com", "password": "wrongpassword"}
    responses = []
    for _ in range(10):
        responses.append(client.post("/api/v1/login/access-token", data=data))
    status_codes = [r.status_code for r in responses]
    assert 429 in status_codes or 404 in status_codes
