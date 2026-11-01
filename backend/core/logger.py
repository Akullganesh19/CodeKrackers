import logging
import sys

import structlog

import re

def mask_email(match):
    email = match.group(0)
    parts = email.split('@')
    if len(parts) == 2 and len(parts[0]) > 0:
        return f"{parts[0][0]}***@{parts[1]}"
    return "***REDACTED***"

def mask_phone(match):
    phone = match.group(0)
    if len(phone) > 4:
        return f"***-***-{phone[-4:]}"
    return "***REDACTED***"

def redact_sensitive_data(logger, method_name, event_dict):
    SENSITIVE_KEYS = {"password", "secret", "otp", "token", "ssn", "address"}

    for key, value in list(event_dict.items()):
        if isinstance(key, str):
            key_lower = key.lower()
            if any(sensitive in key_lower for sensitive in SENSITIVE_KEYS):
                event_dict[key] = "***REDACTED***"
            elif "email" in key_lower and isinstance(value, str):
                parts = value.split('@')
                if len(parts) == 2 and len(parts[0]) > 0:
                    event_dict[key] = f"{parts[0][0]}***@{parts[1]}"
                else:
                    event_dict[key] = "***REDACTED***"
            elif "phone" in key_lower and isinstance(value, (str, int)):
                value = str(value)
                if len(value) > 4:
                    event_dict[key] = f"***-***-{value[-4:]}"
                else:
                    event_dict[key] = "***REDACTED***"

    if "event" in event_dict and isinstance(event_dict["event"], str):
        event_str = event_dict["event"]

        # Redact emails
        event_str = re.sub(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', mask_email, event_str)
        # Redact phone numbers (simple regex, maybe just 10-15 digits with optional plus)
        event_str = re.sub(r'\+?\d{10,15}', mask_phone, event_str)

        event_dict["event"] = event_str

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
