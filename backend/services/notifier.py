import logging
from twilio.rest import Client
from backend.core.config import settings
from backend.core.resilience import CircuitBreaker

logger = logging.getLogger("vas.notifier")

def fallback_send_threat_alert(phone_number: str, threat_type: str, score: float, original_sender: str) -> bool:
    logger.warning(f"Circuit Breaker OPEN: Skipping Twilio SMS to {phone_number}")
    return False

@CircuitBreaker(failure_threshold=3, recovery_timeout_sec=60.0, fallback=fallback_send_threat_alert)
def send_threat_alert(phone_number: str, threat_type: str, score: float, original_sender: str) -> bool:
    """
    Sends a high-priority alert notification to the user's phone via Twilio SMS.
    """
    if not all([settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN, settings.TWILIO_PHONE_NUMBER]):
        logger.warning("Twilio credentials missing. Notification skipped.")
        return False

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


def fallback_send_sms_otp(phone_number: str, otp_code: str) -> bool:
    logger.warning(f"Circuit Breaker OPEN: Skipping OTP SMS to {phone_number}")
    return False

@CircuitBreaker(failure_threshold=3, recovery_timeout_sec=60.0, fallback=fallback_send_sms_otp)
def _send_sms_otp(phone_number: str, otp_code: str) -> bool:
    if not all([settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN, settings.TWILIO_PHONE_NUMBER]):
        return False

    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

    msg_body = (
        f"VAS Command Center: Your verification code is {otp_code}. "
        "Valid for 5 minutes. DO NOT share this with anyone."
    )

    client.messages.create(
        body=msg_body,
        from_=settings.TWILIO_PHONE_NUMBER,
        to=phone_number
    )

    logger.info(f"OTP sent to {phone_number}")
    return True

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

    success = _send_sms_otp(phone_number, otp_code)
    if not success:
        logger.warning(f"FALLBACK SIMULATED OTP: {otp_code}")

    return otp_code
