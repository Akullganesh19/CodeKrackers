import re
import structlog

# Compile regex patterns once
_EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b')
_PHONE_PATTERN = re.compile(r'\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b')
_PURE_DIGIT_PHONE = re.compile(r'\b\+?\d{10,15}\b')
_OTP_PATTERN = re.compile(r'(->\s*)(\d{4,8})\b')

def _redact_email(match):
    email = match.group(0)
    parts = email.split('@')
    if len(parts) == 2:
        username, domain = parts
        return f"{username[0]}***@{domain}"
    return "[REDACTED EMAIL]"

def _redact_phone(match):
    phone = match.group(0)
    # Avoid redacting small numbers like "1234567"
    digits = re.sub(r'\D', '', phone)
    if len(digits) < 10:
        return phone
    if len(phone) > 4:
        # keep optional prefix like +, but redact middle
        if phone.startswith('+'):
            return f"+***{phone[-4:]}"
        return f"***{phone[-4:]}"
    return "***"

def _redact_pure_digits(match):
    phone = match.group(0)
    if len(phone) > 4:
        if phone.startswith('+'):
            return f"+***{phone[-4:]}"
        return f"***{phone[-4:]}"
    return "***"

def _redact_otp(match):
    return f"{match.group(1)}[REDACTED]"

def redact_string(value: str) -> str:
    if not isinstance(value, str):
        return value

    value = _EMAIL_PATTERN.sub(_redact_email, value)
    value = _PHONE_PATTERN.sub(_redact_phone, value)
    value = _PURE_DIGIT_PHONE.sub(_redact_pure_digits, value)
    value = _OTP_PATTERN.sub(_redact_otp, value)

    return value

def redact_pii(logger, log_method, event_dict):
    """
    Structlog processor to redact sensitive PII (emails, phone numbers, OTPs) from logs.
    """
    for key, value in event_dict.items():
        if isinstance(value, str):
            event_dict[key] = redact_string(value)
        # Also redact inside common nested structures like exception/traceback strings
        elif isinstance(value, dict):
            for sub_key, sub_val in value.items():
                if isinstance(sub_val, str):
                    value[sub_key] = redact_string(sub_val)

    return event_dict
