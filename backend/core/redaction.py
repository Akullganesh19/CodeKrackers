import re
from typing import Any

EMAIL_REGEX = re.compile(r"([a-zA-Z0-9_.+-]+)@([a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)")
PHONE_REGEX = re.compile(r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b")
OTP_REGEX = re.compile(r"(?:OTP|code|Code|PIN|pin)(?:\s+(?:is|for.*?->)?\s*|\s*:\s*|\s+)(\d{6})(?!\d)")

def mask_email(match) -> str:
    user = match.group(1)
    domain = match.group(2)
    if len(user) > 1:
        return f"{user[0]}***@{domain}"
    return f"***@{domain}"

def mask_phone(match) -> str:
    phone = match.group(0)
    digits = re.sub(r"\D", "", phone)
    if len(digits) >= 4:
        return f"***-***-{digits[-4:]}"
    return "***-***-****"

def redact_string(text: str) -> str:
    if not isinstance(text, str):
        return str(text)
    text = EMAIL_REGEX.sub(mask_email, text)
    text = PHONE_REGEX.sub(mask_phone, text)
    text = OTP_REGEX.sub(lambda m: m.group(0).replace(m.group(1), "[REDACTED_OTP]"), text)
    return text

def redact_data(data: Any) -> Any:
    """Recursively redact sensitive patterns in strings, lists, and dicts."""
    if isinstance(data, str):
        return redact_string(data)
    elif isinstance(data, dict):
        return {k: redact_data(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [redact_data(v) for v in data]
    return data
