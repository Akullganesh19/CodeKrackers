from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from backend.core.config import settings
from backend.core.resilience import with_retries, circuit_breaker

@with_retries(max_retries=3, base_delay=0.5, exceptions=(TwilioRestException,))
@circuit_breaker(failure_threshold=5, recovery_timeout=60.0, exceptions=(TwilioRestException,))
def send_alert_sms(to_number: str, message_body: str):
    """
    Send an alert SMS using Twilio.
    """
    if not all([settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN, settings.TWILIO_PHONE_NUMBER]):
        print("Twilio credentials not fully configured. Skipping SMS.")
        return None
    
    try:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=message_body,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=to_number
        )
        return message.sid
    except Exception as e:
        print(f"Twilio SMS Error: {e}")
        return None
