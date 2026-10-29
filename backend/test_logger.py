import pytest
from backend.core.logger import redact_sensitive_data

def test_redact_sensitive_data():
    event_dict = {
        "event": "SECURITY: Generated OTP for jdoe@gmail.com -> 123456",
        "password": "mysecretpassword",
        "otp": "123456"
    }

    redacted = redact_sensitive_data(None, None, event_dict)

    assert redacted["password"] == "***"
    assert redacted["otp"] == "***"

def test_redact_phone():
    event_dict = {
        "event": "SIMULATED OTP SENT TO +919876543210: 654321",
    }
    redacted = redact_sensitive_data(None, None, event_dict)
    assert "+9198***210" in redacted["event"]
    assert "76543" not in redacted["event"]

def test_redact_phone_no_country_code():
    event_dict = {
        "event": "Auth failure: Invalid OTP attempt for 9876543210",
    }
    redacted = redact_sensitive_data(None, None, event_dict)
    assert "98***210" in redacted["event"]
