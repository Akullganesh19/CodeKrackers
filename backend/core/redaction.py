import re
from typing import Any

# Regex patterns for sensitive data
EMAIL_REGEX = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b')
PHONE_REGEX = re.compile(r'\b(?:\+?\d{1,3}[-.\s]?)?\d{10}\b')
OTP_REGEX = re.compile(r'(?i)(OTP|code.*?|->\s*)([0-9]{4,6})\b')

def redact_string(text: Any) -> str:
    """
    Redacts PII (emails, phone numbers, OTPs) from a given string.
    If the input is not a string, it converts it to one.
    """
    if not isinstance(text, str):
        try:
            text = str(text)
        except Exception:
            return "[UNREDACTABLE_OBJECT]"

    def redact_email(match):
        email = match.group(0)
        parts = email.split('@')
        if len(parts) == 2:
            # Keep first character of username, mask the rest
            return f"{parts[0][0]}***@{parts[1]}"
        return "[REDACTED_EMAIL]"

    def redact_phone(match):
        phone = match.group(0)
        # Keep only the last 4 digits
        return f"***-***-{phone[-4:]}" if len(phone) >= 4 else "[REDACTED_PHONE]"

    def redact_otp(match):
        prefix = match.group(1)
        # The first group contains the contextual word (e.g. 'OTP', 'code:', '-> ')
        return f"{prefix}[REDACTED_OTP]"

    # Apply redactions
    text = EMAIL_REGEX.sub(redact_email, text)
    text = PHONE_REGEX.sub(redact_phone, text)
    text = OTP_REGEX.sub(redact_otp, text)

    return text
