from backend.core.redaction import redact_string, redact_dict


def test_redact_string():
    s = "User john@example.com logged in. Phone: +1-800-555-1234, OTP: 123456. Timestamp 1691234567."
    r = redact_string(s)
    assert "john@example.com" not in r
    assert "j***@example.com" in r
    assert "+1-800-555-1234" not in r
    assert "OTP: [REDACTED]" in r
    assert "1691234567" in r  # timestamp should NOT be redacted


def test_redact_dict():
    d = {
        "user_email": "john@example.com",
        "phone_number": "+1-800-555-1234",
        "other": "test",
    }
    r = redact_dict(d)
    assert r["user_email"] == "[REDACTED]"
    assert r["phone_number"] == "[REDACTED]"
    assert r["other"] == "test"
