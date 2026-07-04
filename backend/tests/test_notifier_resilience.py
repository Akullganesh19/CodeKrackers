from unittest.mock import patch
from backend.services.notifier import send_threat_alert
from backend.core.resilience import CircuitBreakerOpenException

def test_circuit_breaker_on_twilio_failure():
    with patch("backend.services.notifier.Client") as MockClient:
        mock_client = MockClient.return_value
        mock_client.messages.create.side_effect = Exception("Twilio Error")

        with patch("backend.services.notifier.settings") as mock_settings:
            mock_settings.TWILIO_ACCOUNT_SID = "test"
            mock_settings.TWILIO_AUTH_TOKEN = "test"
            mock_settings.TWILIO_PHONE_NUMBER = "test"

            try:
                # Should fail directly first 3 times, retries happen under the hood
                send_threat_alert("123", "scam", 0.9, "badguy")
            except Exception:
                pass
            try:
                send_threat_alert("123", "scam", 0.9, "badguy")
            except Exception:
                pass
            try:
                send_threat_alert("123", "scam", 0.9, "badguy")
            except Exception:
                pass

            # 4th time circuit is open
            try:
                send_threat_alert("123", "scam", 0.9, "badguy")
                assert False, "Should have raised CircuitBreakerOpenException"
            except CircuitBreakerOpenException:
                pass
            except Exception:
                assert False, "Should have raised CircuitBreakerOpenException"
