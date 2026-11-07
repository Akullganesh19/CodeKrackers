import logging
import sys

import structlog
import re

OTP_REGEX = re.compile(r'\b\d{6}\b')
EMAIL_REGEX = re.compile(r'\b([a-zA-Z0-9._%+-])([a-zA-Z0-9._%+-]*)@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b')
PHONE_REGEX = re.compile(r'(?<!\d)\+?\d{10,15}(?!\d)')

SENSITIVE_KEYS = {"password", "secret", "otp", "token", "ssn"}
PII_KEYS = {"email", "phone"}

def mask_email(match):
    first_char = match.group(1)
    return f"{first_char}***@{match.group(3)}"

def mask_phone(match):
    val = match.group(0)
    if len(val) > 4:
        return f"{val[:-4]}****"
    return "****"

def redact_sensitive_data(logger, log_method, event_dict):
    if "event" in event_dict and isinstance(event_dict["event"], str):
        event_str = event_dict["event"]
        event_str = OTP_REGEX.sub("[REDACTED]", event_str)
        event_str = EMAIL_REGEX.sub(mask_email, event_str)
        event_str = PHONE_REGEX.sub(mask_phone, event_str)
        event_dict["event"] = event_str

    for key, value in list(event_dict.items()):
        if isinstance(key, str):
            key_lower = key.lower()
            if any(s in key_lower for s in SENSITIVE_KEYS):
                event_dict[key] = "[REDACTED]"
            elif any(p in key_lower for p in PII_KEYS):
                if isinstance(value, str):
                    if "@" in value:
                        event_dict[key] = EMAIL_REGEX.sub(mask_email, value)
                    else:
                        event_dict[key] = PHONE_REGEX.sub(mask_phone, value)
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
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        redact_sensitive_data,
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
