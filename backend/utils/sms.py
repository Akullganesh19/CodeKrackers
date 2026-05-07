from twilio.rest import Client
from backend.core.config import settings

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
