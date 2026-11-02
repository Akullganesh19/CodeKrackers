import logging
import sys

import structlog

import re

def redact_email_str(email: str) -> str:
    parts = str(email).split('@')
    if len(parts) == 2 and len(parts[0]) > 0:
        return f"{parts[0][0]}***@{parts[1]}"
    return "[REDACTED]"

def redact_phone_str(phone: str) -> str:
    phone = str(phone)
    if len(phone) >= 5:
        return phone[:3] + "***" + phone[-2:]
    return "[REDACTED]"

def redact_string(s: str) -> str:
    if not isinstance(s, str):
        return s
    s = re.sub(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', lambda m: redact_email_str(m.group(0)), s)
    s = re.sub(r'(?<!\d)\+?\d{10,15}(?!\d)', lambda m: redact_phone_str(m.group(0)), s)
    s = re.sub(r'(?:OTP|Code|code|->|:)[^\d]*(\b\d{6}\b)', lambda m: m.group(0).replace(m.group(1), '***'), s, flags=re.IGNORECASE)
    return s

def redact_sensitive_data(logger, method_name, event_dict):
    SENSITIVE_KEYS = {"email", "phone", "password", "otp", "code", "ssn", "identifier", "username", "phone_number"}
    for key, val in list(event_dict.items()):
        if not isinstance(key, str):
            continue
        key_lower = key.lower()
        is_sensitive_key = any(sens in key_lower for sens in SENSITIVE_KEYS)
        if is_sensitive_key:
            if "email" in key_lower and isinstance(val, str) and '@' in val:
                event_dict[key] = redact_email_str(val)
            elif "phone" in key_lower and isinstance(val, str):
                event_dict[key] = redact_phone_str(val)
            else:
                event_dict[key] = "[REDACTED]"
        elif isinstance(val, str):
            event_dict[key] = redact_string(val)
    return event_dict


def setup_logging(json_logs: bool = True, log_level: int = logging.INFO):
    """
    Configure standard logging and structlog.
    """
    # Configure standard logging to route through structlog
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )

    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        redact_sensitive_data,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    if json_logs:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())

    structlog.configure(
        processors=processors,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

def get_logger(name: str):
    """
    Returns a structlog configured logger.
    """
    return structlog.get_logger(name)
