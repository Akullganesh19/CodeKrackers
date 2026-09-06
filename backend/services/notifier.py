import logging

from twilio.rest import Client

from backend.core.config import settings
from backend.core.resilience import CircuitBreaker, with_retry_sync

logger = logging.getLogger("vas.notifier")


@CircuitBreaker(failure_threshold=3, cooldown_seconds=60)
@with_retry_sync(max_attempts=3, initial_backoff=0.5)
def _send_twilio_alert(
    phone_number: str, threat_type: str, score: float, original_sender: str
):
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

    alert_msg = (
        f"🚨 VAS SECURITY ALERT 🚨\n\n"
        f"Red Flag detected from: {original_sender}\n"
        f"Threat Type: {threat_type}\n"
        f"Risk Score: {round(score * 100)}%\n\n"
        f"⚠️ DO NOT click any links or share OTPs. This message has been logged for evidence."
    )

    message = client.messages.create(
        body=alert_msg, from_=settings.TWILIO_PHONE_NUMBER, to=phone_number
    )

    logger.info(f"Notification sent to {phone_number}. SID: {message.sid}")
    return True


def send_threat_alert(
    phone_number: str, threat_type: str, score: float, original_sender: str
):
    """
    Sends a high-priority alert notification to the user's phone via Twilio SMS.
    """
    if not all(
        [
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN,
            settings.TWILIO_PHONE_NUMBER,
        ]
    ):
        logger.warning("Twilio credentials missing. Notification skipped.")
        return False

    try:
        return _send_twilio_alert(phone_number, threat_type, score, original_sender)
    except Exception as e:
        logger.error(f"Failed to send notification: {e}")
        return False


@CircuitBreaker(failure_threshold=3, cooldown_seconds=60)
@with_retry_sync(max_attempts=3, initial_backoff=0.5)
def _send_twilio_otp(phone_number: str, otp_code: str) -> str:
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

    msg_body = (
        f"VAS Command Center: Your verification code is {otp_code}. "
        "Valid for 5 minutes. DO NOT share this with anyone."
    )

    client.messages.create(
        body=msg_body, from_=settings.TWILIO_PHONE_NUMBER, to=phone_number
    )

    logger.info(f"OTP sent to {phone_number}")
    return otp_code


def send_otp(phone_number: str) -> str:
    """
    Sends a 6-digit OTP code to the user.
    Returns the generated code for validation.
    """
    import random

    otp_code = str(random.randint(100000, 999999))

    if not all(
        [
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN,
            settings.TWILIO_PHONE_NUMBER,
        ]
    ):
        logger.warning(f"SIMULATED OTP SENT TO {phone_number}: {otp_code}")
        print(f"\n[VAS AUTH] SMS OTP for {phone_number}: {otp_code}\n")
        return otp_code

    try:
        return _send_twilio_otp(phone_number, otp_code)
    except Exception as e:
        logger.error(f"Failed to send OTP: {e}")
        # Fallback to simulation in logs for dev convenience
        logger.warning(f"FALLBACK SIMULATED OTP: {otp_code}")
        return otp_code
