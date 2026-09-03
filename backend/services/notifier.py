import logging
from twilio.rest import Client
from backend.core.config import settings
from backend.core.resilience import CircuitBreaker, with_retry_sync

logger = logging.getLogger("vas.notifier")


class DummyMessage:
    def __init__(self):
        self.sid = "fallback_sid"


def twilio_fallback(*args, **kwargs):
    logger.error("Twilio Circuit Open, fallback triggered (SMS not sent)")
    return DummyMessage()


@CircuitBreaker(failure_threshold=3, recovery_timeout=120.0, fallback=twilio_fallback)
@with_retry_sync(max_retries=3, base_delay=1.0)
def _do_twilio_request(client, body, from_, to):
    message = client.messages.create(body=body, from_=from_, to=to)
    # The client throws TwilioRestException on 4xx/5xx HTTP errors
    # Which will be caught by the retry logic
    return message


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
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

        alert_msg = (
            f"🚨 VAS SECURITY ALERT 🚨\n\n"
            f"Red Flag detected from: {original_sender}\n"
            f"Threat Type: {threat_type}\n"
            f"Risk Score: {round(score * 100)}%\n\n"
            f"⚠️ DO NOT click any links or share OTPs. This message has been logged for evidence."
        )

        message = _do_twilio_request(
            client=client,
            body=alert_msg,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=phone_number,
        )

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
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

        msg_body = (
            f"VAS Command Center: Your verification code is {otp_code}. "
            "Valid for 5 minutes. DO NOT share this with anyone."
        )

        _do_twilio_request(
            client=client,
            body=msg_body,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=phone_number,
        )

        logger.info(f"OTP sent to {phone_number}")
        return otp_code
    except Exception as e:
        logger.error(f"Failed to send OTP: {e}")
        # Fallback to simulation in logs for dev convenience
        logger.warning(f"FALLBACK SIMULATED OTP: {otp_code}")
        return otp_code
