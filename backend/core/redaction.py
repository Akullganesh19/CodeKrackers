import logging
import re
from typing import Any

EMAIL_PATTERN = re.compile(r'\b[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+\b')

def mask_email(match: re.Match) -> str:
    email = match.group(0)
    parts = email.split('@')
    if len(parts) == 2:
        name, domain = parts
        masked_name = name[0] + "***" if len(name) > 1 else "***"
        return f"{masked_name}@{domain}"
    return "[REDACTED EMAIL]"

# Requires common formatting characters (+, -, (), spaces) to avoid 10-digit timestamps
PHONE_PATTERN = re.compile(
    r'(?:'
    r'\+\d{10,15}\b'
    r'|'
    r'\b(?:\+\d{1,3}[\s.-]+)?\(?\d{3}\)?[\s.-]+\d{3}[\s.-]+\d{4}\b'
    r')'
)

# Requires prefixes like "otp" or "code" to avoid accidental redaction of harmless 6-digit integers
OTP_PATTERN = re.compile(r'(?i)(\b(?:otp|code)[^\d]{0,10}?)(\d{6})\b')

def mask_otp(match: re.Match) -> str:
    return f"{match.group(1)}[REDACTED OTP]"

def redact_string(text: str) -> str:
    if not isinstance(text, str):
        return str(text)
    text = EMAIL_PATTERN.sub(mask_email, text)
    text = PHONE_PATTERN.sub("[REDACTED PHONE]", text)
    text = OTP_PATTERN.sub(mask_otp, text)
    return text

SENSITIVE_KEYS = {'otp', 'password', 'phone', 'ssn', 'email', 'card_number', 'dob', 'date_of_birth', 'identifier'}

def redact_dict(data: Any) -> Any:
    if isinstance(data, dict):
        redacted = {}
        for k, v in data.items():
            k_lower = str(k).lower()
            if any(sensitive_key in k_lower for sensitive_key in SENSITIVE_KEYS):
                if "email" in k_lower and isinstance(v, str) and '@' in v:
                    redacted[k] = EMAIL_PATTERN.sub(mask_email, v)
                else:
                    redacted[k] = "[REDACTED]"
            else:
                redacted[k] = redact_dict(v)
        return redacted
    elif isinstance(data, list) or isinstance(data, tuple):
        return type(data)(redact_dict(item) for item in data)
    elif isinstance(data, str):
        return redact_string(data)
    else:
        return data

def structlog_redactor(logger: Any, method_name: str, event_dict: Any) -> Any:
    """Structlog processor for redacting sensitive fields."""
    return redact_dict(event_dict)

class RedactingFormatter(logging.Formatter):
    """Custom standard logging formatter that applies string redaction."""
    def format(self, record: logging.LogRecord) -> str:
        original_msg = super().format(record)
        return redact_string(original_msg)
