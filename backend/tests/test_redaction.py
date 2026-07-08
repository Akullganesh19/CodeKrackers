from backend.core.redaction import redact_pii

def test_redact_pii_emails():
    event = {"event": "hello john.doe@example.com"}
    redact_pii(None, None, event)
    assert event["event"] == "hello j***@example.com"

def test_redact_pii_phones():
    event = {"event": "call +15551234567 or 15551234567"}
    redact_pii(None, None, event)
    assert event["event"] == "call +***4567 or ***4567"

def test_redact_pii_otp():
    event = {"event": "Generated OTP for test@test.com -> 123456"}
    redact_pii(None, None, event)
    assert event["event"] == "Generated OTP for t***@test.com -> [REDACTED]"
