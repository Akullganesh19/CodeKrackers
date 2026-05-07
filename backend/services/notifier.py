import logging
from twilio.rest import Client
from backend.core.config import settings

logger = logging.getLogger("vas.notifier")

def send_threat_alert(phone_number: str, threat_type: str, score: float, original_sender: str):
    """
    Sends a high-priority alert notification to the user's phone via Twilio SMS.
    """
    if not all([settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN, settings.TWILIO_PHONE_NUMBER]):
        logger.warning("Twilio credentials missing. Notification skipped.")
        return False

    try:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        
        alert_msg = (
            f"🚨 VAS SECURITY ALERT 🚨\n\n"
            f"Red Flag detected from: {original_sender}\n"
            f"Threat Type: {threat_type}\n"
            f"Risk Score: {round(score * 100)}%\n\n"
            f"⚠️ DO NOT click any links or share OTPs. This message has been logged for evidence."
        )

        message = client.messages.create(
            body=alert_msg,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=phone_number
        )
        
        logger.info(f"Notification sent to {phone_number}. SID: {message.sid}")
        return True
    except Exception as e:
        logger.error(f"Failed to send notification: {e}")
        return False
