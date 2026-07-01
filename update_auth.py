import re

with open("backend/api/auth.py", "r") as f:
    content = f.read()

# Add import
import_stmt = "from backend.core.resilience import with_retries, circuit_breaker\n"
if "from backend.core.resilience" not in content:
    content = content.replace("from backend.models.orm import User, UserRole", "from backend.models.orm import User, UserRole\n" + import_stmt)

# Add helpers before send_otp
helpers = """
@with_retries(max_attempts=3, base_delay=0.1)
@circuit_breaker(failure_threshold=3, recovery_timeout=60.0)
def _send_twilio_otp(identifier: str, otp_code: str):
    if not (settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN and settings.TWILIO_PHONE_NUMBER):
        return
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    client.messages.create(
        body=f"VSDP Security Code: {otp_code}. Valid for 5 minutes. Do not share.",
        from_=settings.TWILIO_PHONE_NUMBER,
        to=identifier
    )

@with_retries(max_attempts=3, base_delay=0.1)
@circuit_breaker(failure_threshold=3, recovery_timeout=60.0)
def _send_sendgrid_otp(identifier: str, otp_code: str):
    if not settings.SENDGRID_API_KEY:
        return
    message = Mail(
        from_email=settings.FROM_EMAIL,
        to_emails=identifier,
        subject='VSDP Security Code',
        plain_text_content=f"Your VSDP security code is: {otp_code}. Valid for 5 minutes. Do not share."
    )
    sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
    sg.send(message)

"""

if "_send_twilio_otp" not in content:
    content = content.replace("@router.post(\"/send\")", helpers + "\n@router.post(\"/send\")")

# Modify send_otp body
search_str = """    if "@" not in otp_in.identifier and settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
        try:
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            client.messages.create(
                body=f"VSDP Security Code: {otp_code}. Valid for 5 minutes. Do not share.",
                from_=settings.TWILIO_PHONE_NUMBER,
                to=otp_in.identifier
            )
        except Exception as e:
            logger.error(f"SMS_GATEWAY_ERROR: Failed to send OTP to {otp_in.identifier}: {e}")

    if "@" in otp_in.identifier and settings.SENDGRID_API_KEY:
        try:
            message = Mail(
                from_email=settings.FROM_EMAIL,
                to_emails=otp_in.identifier,
                subject='VSDP Security Code',
                plain_text_content=f"Your VSDP security code is: {otp_code}. Valid for 5 minutes. Do not share."
            )
            sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
            sg.send(message)
        except Exception as e:
            logger.error(f"EMAIL_GATEWAY_ERROR: Failed to send OTP to {otp_in.identifier}: {e}")"""

replace_str = """    try:
        if "@" not in otp_in.identifier:
            _send_twilio_otp(otp_in.identifier, otp_code)
        else:
            _send_sendgrid_otp(otp_in.identifier, otp_code)
    except Exception as e:
        logger.error(f"GATEWAY_ERROR: Failed to send OTP to {otp_in.identifier} after retries: {e}")
        # Return 503 instead of success if we actually failed to send
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Failed to send OTP due to gateway error. Please try again later."
        )"""

content = content.replace(search_str, replace_str)

with open("backend/api/auth.py", "w") as f:
    f.write(content)
