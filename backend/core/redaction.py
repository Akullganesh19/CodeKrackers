import re
from typing import Any

# Email: mask first character, keep domain
_EMAIL_RE = re.compile(r'\b([A-Za-z0-9._%+-])[A-Za-z0-9._%+-]*(@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})\b', flags=re.IGNORECASE)

def _mask_email(match):
    return f"{match.group(1)}***{match.group(2)}"

# Phone number: require common formatting OR exactly 10 digits not starting with 1
_PHONE_RE = re.compile(
    r'(?:\+\d{1,3}[-.\s])?\(?\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}\b'
    r'|\b(?![1])\d{10}\b'
    r'|\b\+\d{10,15}\b'
)

# OTP / Code: context-aware
_OTP_RE = re.compile(r'\b(otp|code|pin)(?:\s*[:=]\s*|\s+)(\d{4,6})\b', flags=re.IGNORECASE)

def _mask_otp(match):
    prefix = match.group(1)
    sep = match.group(0)[len(prefix):-len(match.group(2))]
    return f"{prefix}{sep}[REDACTED]"

_SENSITIVE_KEYS = {"otp", "password", "phone", "ssn", "phone_number", "email", "identifier", "email_address", "user_email"}

def redact_string(text: str) -> str:
    """Redacts PII (email, phone, OTPs) from a given string."""
    if not isinstance(text, str):
        return text

    text = _EMAIL_RE.sub(_mask_email, text)
    text = _PHONE_RE.sub("[REDACTED]", text)
    text = _OTP_RE.sub(_mask_otp, text)
    return text

def redact_dict(data: Any) -> Any:
    """Recursively redact sensitive keys and string values in dictionaries/lists."""
    if isinstance(data, dict):
        return {k: ("[REDACTED]" if str(k).lower() in _SENSITIVE_KEYS else redact_dict(v)) for k, v in data.items()}
    elif isinstance(data, list):
        return [redact_dict(item) for item in data]
    elif isinstance(data, str):
        return redact_string(data)
    return data
