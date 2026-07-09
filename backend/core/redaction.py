"""Centralized PII redaction utilities."""
import re

EMAIL_PATTERN = re.compile(
    r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)"
)

PHONE_PATTERN = re.compile(
    r"(?<!\d)(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}(?!\d)"
)

OTP_PATTERN = re.compile(r"(?i)(otp(?:.*?)|code(?:.*?)|->\s*)(\b\d{6}\b)")


def redact_email(match) -> str:
    email = match.group(1)
    if "@" in email:
        local, domain = email.split("@", 1)
        if len(local) > 2:
            local = f"{local[0]}***{local[-1]}"
        else:
            local = "***"
        return f"{local}@{domain}"
    return "***@***"


def redact_phone(match) -> str:
    phone = match.group(0)
    digits = re.sub(r"\D", "", phone)
    if len(digits) >= 4:
        return f"***-***-{digits[-4:]}"
    return "***-***-****"


def redact_otp(match) -> str:
    prefix = match.group(1)
    return f"{prefix}******"


def redact_pii(text: str) -> str:
    if not isinstance(text, str):
        return text

    # 1. Redact emails
    text = EMAIL_PATTERN.sub(redact_email, text)

    # 2. Redact phones
    text = PHONE_PATTERN.sub(redact_phone, text)

    # 3. Redact explicit OTPs
    text = OTP_PATTERN.sub(redact_otp, text)

    # 4. Fallback for floating OTPs: if text smells like OTP/code
    if "otp" in text.lower() or "code" in text.lower():
        text = re.sub(r"(?<!\d)(\d{6})(?!\d)", "******", text)

    return text
