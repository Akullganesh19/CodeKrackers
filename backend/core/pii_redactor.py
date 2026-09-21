import re


def mask_email(email: str) -> str:
    parts = email.split("@")
    if len(parts) != 2:
        return email
    username, domain = parts
    if len(username) > 2:
        masked_user = username[0] + "***" + username[-1]
    else:
        masked_user = "***"
    return f"{masked_user}@{domain}"


def mask_phone(phone: str) -> str:
    if len(phone) > 5:
        return phone[:2] + "***" + phone[-4:]
    return "***"


def redact_string(text: str) -> str:
    if not isinstance(text, str):
        return text

    # Redact email
    email_pattern = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
    text = re.sub(email_pattern, lambda m: mask_email(m.group(0)), text)

    # Redact phone (E.164 format)
    # Strictly require the leading + sign
    phone_pattern = r"\B\+[1-9]\d{6,14}\b"
    text = re.sub(phone_pattern, lambda m: mask_phone(m.group(0)), text)

    # Redact OTP code - use more specific pattern to avoid matching all 6-digit IDs
    text = re.sub(r"(OTP.*?)\b(\d{6})\b", r"\1******", text, flags=re.IGNORECASE)

    return text
