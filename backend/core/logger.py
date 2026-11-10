import logging
import sys

import structlog

import re

EMAIL_REGEX = re.compile(r'([a-zA-Z0-9])[a-zA-Z0-9_.+-]*(@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)')
PHONE_REGEX = re.compile(r'(\+?\d{1,3}[-.\s]?)?(\(?\d{3}\)?)[-.\s]?(\d{3})[-.\s]?(\d{4})')
OTP_REGEX = re.compile(r'(OTP.*?->\s*)\d+')

def redact_phone(match):
    prefix = match.group(1) or ""
    area = match.group(2)
    return f"{prefix}{area}-***-****"

def redact_sensitive_data(logger, method_name, event_dict):
    """
    Custom structlog processor to redact sensitive data (PII) from logs.
    """
    sensitive_keys = ['password', 'secret', 'otp', 'code', 'token', 'phone', 'email', 'identifier']

    for key in list(event_dict.keys()):
        if isinstance(key, str):
            lower_key = key.lower()
            if any(sensitive in lower_key for sensitive in sensitive_keys):
                val = event_dict[key]
                if isinstance(val, str) and '@' in val:
                    event_dict[key] = EMAIL_REGEX.sub(r'\1***\2', val)
                elif isinstance(val, str) and sum(c.isdigit() for c in val) >= 10:
                    event_dict[key] = PHONE_REGEX.sub(redact_phone, val)
                else:
                    event_dict[key] = "***"

    # Also apply regex masking directly to the 'event' string
    if 'event' in event_dict and isinstance(event_dict['event'], str):
        event = event_dict['event']
        event = EMAIL_REGEX.sub(r'\1***\2', event)
        event = PHONE_REGEX.sub(redact_phone, event)
        event = OTP_REGEX.sub(r'\g<1>***', event)
        event_dict['event'] = event

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
