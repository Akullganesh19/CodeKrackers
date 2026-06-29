import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.models.orm import UserRole
import json
import uuid

client = TestClient(app)

def test_mass_assignment_privilege_escalation():
    # Attempt to register with 'admin' role
    unique_email = f"hacker_{uuid.uuid4()}@example.com"
    payload = {
        "email": unique_email,
        "password": "Password1!",
        "role": "admin"
    }
    response = client.post("/api/auth/register", json=payload)
    # the server should default it to CITIZEN if it ignores the input
    # or reject it (status 400 or 403 or 422 depending on how strictly we lock it)
    assert response.status_code == 201

    # Login to check the token's role
    login_payload = {
        "email": unique_email,
        "password": "Password1!"
    }
    login_response = client.post("/api/auth/login", json=login_payload)
    assert login_response.status_code == 200
    assert login_response.json()["user"]["role"] != "admin"
    assert login_response.json()["user"]["role"] == "citizen"

def test_otp_role_escalation():
    send_payload = {
        "identifier": "otp_hacker@example.com",
        "role": "admin"
    }
    client.post("/api/auth/send", json=send_payload)

    # Needs redis mocked for verification to pass without real OTP, bypass for now
    pass
