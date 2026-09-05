from twilio.rest import Client

from backend.core.config import settings
from backend.core.resilience import CircuitBreaker, with_retry_sync

twilio_sms_cb = CircuitBreaker(failure_threshold=3, recovery_timeout=60.0)


@twilio_sms_cb
@with_retry_sync(max_attempts=3, initial_backoff=0.5)
def _send_alert_sms_twilio(client, message_body: str, to_number: str):
    message = client.messages.create(
        body=message_body, from_=settings.TWILIO_PHONE_NUMBER, to=to_number
    )
    return message.sid


def send_alert_sms(to_number: str, message_body: str):
    """
    Send an alert SMS using Twilio.
    """
    if not all(
        [
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN,
            settings.TWILIO_PHONE_NUMBER,
        ]
    ):
        print("Twilio credentials not fully configured. Skipping SMS.")
        return None

    try:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        sid = _send_alert_sms_twilio(client, message_body, to_number)
        return sid
    except Exception as e:
        print(f"Twilio SMS Error: {e}")
        return None
