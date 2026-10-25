import re
import structlog

EMAIL_RE = re.compile(r'\b([a-zA-Z0-9._%+-])([a-zA-Z0-9._%+-]*)?(@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b')
PHONE_RE = re.compile(r'(?<!\d)(\+?\d{1,3}[-.\s]?)?\(?(\d{3})\)?[-.\s]?(\d{3})[-.\s]?(\d{4})(?!\d)')
OTP_RE = re.compile(r'(?i)(otp|code(?: is)?|->|:)\s*:?\s*(\b\d{6}\b)')

def redact_email(match):
    return match.group(1) + "***" + match.group(3)

def redact_phone(match):
    prefix = match.group(1) or ""
    return prefix + "***-***-" + match.group(4)

def redact_otp(match):
    return match.group(1) + " [REDACTED]"

def redact_string(msg: str) -> str:
    msg = EMAIL_RE.sub(redact_email, msg)
    msg = PHONE_RE.sub(redact_phone, msg)
    msg = OTP_RE.sub(redact_otp, msg)
    return msg

def redact_sensitive_data(logger, log_method, event_dict):
    """
    Structlog processor to redact emails, phone numbers, and OTPs
    from log messages and kwargs before they are written.
    """
    # Check all keys in event_dict to cover event, kwargs, and context vars
    for key, value in event_dict.items():
        if isinstance(value, str):
            event_dict[key] = redact_string(value)

    if 'positional_args' in event_dict:
        args = list(event_dict['positional_args'])
        for i, arg in enumerate(args):
            if isinstance(arg, str):
                args[i] = redact_string(arg)
        event_dict['positional_args'] = tuple(args)

    return event_dict
