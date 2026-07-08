import logging

from twilio.rest import Client

from backend.core.config import settings
from backend.core.resilience import circuit_breaker, with_retries

logger = logging.getLogger("vas.notifier")


@circuit_breaker(failure_threshold=3, recovery_timeout=60)
@with_retries(max_attempts=3, base_delay=1.0)
def _twilio_send_message(body: str, to: str, from_: str) -> str:
    """Internal helper to send Twilio messages with resilience."""
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    message = client.messages.create(body=body, from_=from_, to=to)
    return message.sid


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

    alert_msg = (
        f"🚨 VAS SECURITY ALERT 🚨\n\n"
        f"Red Flag detected from: {original_sender}\n"
        f"Threat Type: {threat_type}\n"
        f"Risk Score: {round(score * 100)}%\n\n"
        f"⚠️ DO NOT click any links or share OTPs. This message has been logged for evidence."
    )

    try:
        sid = _twilio_send_message(
            body=alert_msg, from_=settings.TWILIO_PHONE_NUMBER, to=phone_number
        )
        logger.info(f"Notification sent to {phone_number}. SID: {sid}")
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

    msg_body = (
        f"VAS Command Center: Your verification code is {otp_code}. "
        "Valid for 5 minutes. DO NOT share this with anyone."
    )

    try:
        _twilio_send_message(
            body=msg_body, from_=settings.TWILIO_PHONE_NUMBER, to=phone_number
        )
        logger.info(f"OTP sent to {phone_number}")
        return otp_code
    except Exception as e:
        logger.error(f"Failed to send OTP: {e}")
        # Fallback to simulation in logs for dev convenience
        logger.warning(f"FALLBACK SIMULATED OTP: {otp_code}")
        return otp_code
