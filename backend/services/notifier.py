import logging
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from backend.core.config import settings
from backend.core.resilience import with_retries

logger = logging.getLogger("vas.notifier")

@with_retries(max_attempts=3, base_delay=1.0, max_delay=4.0, exceptions=(TwilioRestException, Exception))
def _send_alert(client, alert_msg, phone_number):
    return client.messages.create(
        body=alert_msg,
        from_=settings.TWILIO_PHONE_NUMBER,
        to=phone_number
    )

@with_retries(max_attempts=3, base_delay=1.0, max_delay=4.0, exceptions=(TwilioRestException, Exception))
def _send_otp_sms(client, msg_body, phone_number):
    return client.messages.create(
        body=msg_body,
        from_=settings.TWILIO_PHONE_NUMBER,
        to=phone_number
    )

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

        message = _send_alert(client, alert_msg, phone_number)
        
        logger.info(f"Notification sent to {phone_number}. SID: {message.sid}")
        return True
    except Exception as e:
        logger.error(f"Failed to send notification: {e}")
        return False

def send_otp(phone_number: str) -> str:
    """
    Sends a 6-digit OTP code to the user.
    Returns the generated code for validation.
    """
    import random
    otp_code = str(random.randint(100000, 999999))
    
    if not all([settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN, settings.TWILIO_PHONE_NUMBER]):
        logger.warning(f"SIMULATED OTP SENT TO {phone_number}: {otp_code}")
        print(f"\n[VAS AUTH] SMS OTP for {phone_number}: {otp_code}\n")
        return otp_code

    try:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        
        msg_body = (
            f"VAS Command Center: Your verification code is {otp_code}. "
            "Valid for 5 minutes. DO NOT share this with anyone."
        )

        _send_otp_sms(client, msg_body, phone_number)
        
        logger.info(f"OTP sent to {phone_number}")
        return otp_code
    except Exception as e:
        logger.error(f"Failed to send OTP: {e}")
        # Fallback to simulation in logs for dev convenience
        logger.warning(f"FALLBACK SIMULATED OTP: {otp_code}")
        return otp_code
