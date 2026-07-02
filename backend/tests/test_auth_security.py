import uuid

from fastapi.testclient import TestClient
from unittest.mock import patch
from backend.main import app

client = TestClient(app)


def test_register_role_escalation():
    """Test that a user cannot escalate their role during registration."""
    # Attempt to register with a super_admin role
    # Use random email to avoid collision with previous test runs
    email = f"hacker_escalate_{uuid.uuid4().hex[:8]}@example.com"
    with patch("backend.core.security.get_password_hash", return_value="dummy_hash"):
        res = client.post(
            "/api/auth/register",
            json={"email": email, "password": "Password1!@", "role": "super_admin"},
        )

        assert res.status_code == 201, f"Registration failed: {res.text}"

        with patch("backend.core.security.verify_password", return_value=True):
            res_login = client.post(
                "/api/auth/login", json={"email": email, "password": "Password1!@"}
            )

            assert res_login.status_code == 200, "Login failed"
            assert res_login.json()["user"]["role"] == "citizen"


def test_register_phone_number_crash():
    """Test that registering with a phone number does not cause a 500 server error."""
    email = f"hacker_phone_{uuid.uuid4().hex[:8]}@example.com"
    phone_number = f"123{uuid.uuid4().hex[:7]}"  # Use random phone number
    with patch("backend.core.security.get_password_hash", return_value="dummy_hash"):
        res = client.post(
            "/api/auth/register",
            json={
                "email": email,
                "password": "Password1!@",
                "phone_number": phone_number,
            },
        )

        assert (
            res.status_code == 201
        ), f"Expected 201 Created, got {res.status_code} - {res.text}"


def test_verify_otp_redis_down_crash():
    """Test that verifying OTP when redis is down doesn't cause a 500 crash."""
    with patch("backend.api.auth.redis_client", None):
        res = client.post(
            "/api/auth/verify",
            json={"identifier": "1234567891", "code": "123456", "role": "super_admin"},
        )

        # Should return a 400 Bad Request (Invalid OTP) rather than crashing with 500
        assert (
            res.status_code == 400
        ), f"Expected 400 Bad Request, got {res.status_code} - {res.text}"
