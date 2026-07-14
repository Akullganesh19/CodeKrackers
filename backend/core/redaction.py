import re
import logging
from typing import Any

EMAIL_REGEX = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")

# Safer phone regex: explicitly requires formatting chars (+, (), -) to prevent catching raw timestamps/IDs.
# It matches:
# - + followed by digits and optional separators
# - (XXX) XXX-XXXX
# - XXX-XXX-XXXX or XXX.XXX.XXXX
PHONE_REGEX = re.compile(r"(?:\+\d{1,3}[\s.-]?)?\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}\b|(?:\+\d{1,3}[\s.-]?)\d{10}\b")
OTP_CONTEXT_REGEX = re.compile(r"(?i)(otp|code|->)([\s=:]+)(\d{6})\b")

# Keys that inherently imply PII, regardless of string structure
SENSITIVE_KEYS = {"otp", "password", "phone", "phone_number", "ssn", "social_security_number", "card_number", "credit_card"}

def is_sensitive_key(key: str) -> bool:
    key_lower = key.lower()
    for sensitive in SENSITIVE_KEYS:
        if sensitive in key_lower:
            return True
    return False

def get_redacted_value_for_key(key: str) -> str:
    key_lower = key.lower()
    if "otp" in key_lower:
        return "[REDACTED_OTP]"
    if "phone" in key_lower:
        return "[REDACTED_PHONE]"
    if "email" in key_lower:
        return "[REDACTED_EMAIL]"
    return "[REDACTED]"

def redact_string(text: str) -> str:
    if not isinstance(text, str):
        return text

    def replace_email(match):
        email = match.group(0)
        parts = email.split('@')
        if len(parts) == 2:
            name, domain = parts
            if len(name) > 1:
                return f"{name[0]}***@{domain}"
            return f"***@{domain}"
        return "[REDACTED_EMAIL]"

    text = EMAIL_REGEX.sub(replace_email, text)
    text = PHONE_REGEX.sub("[REDACTED_PHONE]", text)
    text = OTP_CONTEXT_REGEX.sub(r"\g<1>\g<2>[REDACTED_OTP]", text)

    return text

def redact_dict(data: dict) -> dict:
    result = {}
    for key, value in data.items():
        key_str = str(key)

        if is_sensitive_key(key_str):
            result[key] = get_redacted_value_for_key(key_str)
            continue

        if isinstance(value, str):
            result[key] = redact_string(value)
        elif isinstance(value, dict):
            result[key] = redact_dict(value)
        elif isinstance(value, list):
            result[key] = [get_redacted_value_for_key(key_str) if is_sensitive_key(key_str) else redact_string(v) if isinstance(v, str) else redact_dict(v) if isinstance(v, dict) else v for v in value]
        else:
            result[key] = value

    return result

def redact_structlog(logger, method_name, event_dict):
    return redact_dict(event_dict)

class RedactingFormatter(logging.Formatter):
    def format(self, record):
        original = super().format(record)
        return redact_string(original)
