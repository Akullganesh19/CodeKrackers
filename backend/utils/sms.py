from backend.core.config import settings
from backend.core.resilience import with_retries, circuit_breaker

@circuit_breaker(failure_threshold=3, recovery_timeout=60.0)
@with_retries(max_attempts=3, base_delay=0.5)
def send_alert_sms(to_number: str, message_body: str):
    """
    Send an alert SMS using Twilio.
    """
    from twilio.rest import Client
    if not all([settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN, settings.TWILIO_PHONE_NUMBER]):
        print("Twilio credentials not fully configured. Skipping SMS.")
        return None
    
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    message = client.messages.create(
        body=message_body,
        from_=settings.TWILIO_PHONE_NUMBER,
        to=to_number
    )
    return message.sid
