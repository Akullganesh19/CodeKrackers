import logging
import sys
import re

import structlog

EMAIL_REGEX = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")

def redact_string(s: str) -> str:
    def mask_email(match):
        email = match.group(0)
        if "@" in email:
            name, domain = email.split("@", 1)
            masked_name = name[0] + "***" if len(name) > 0 else "***"
            return f"{masked_name}@{domain}"
        return "***"

    def mask_phone(match):
        prefix = match.group(1)
        phone = match.group(2)
        if len(phone) >= 6:
            return f"{prefix}{phone[:3]}***{phone[-2:]}"
        return f"{prefix}***"

    s = EMAIL_REGEX.sub(mask_email, s)
    # Phone numbers: Use context ("phone=" or "to ") to avoid replacing timestamps or DB IDs
    s = re.sub(r"(?i)(phone\s*=\s*|to\s+|phone_number\s*=\s*)(\+?\d{10,15})(?!\d)", mask_phone, s)
    # OTPs: 6 digits preceded by "OTP" (case insensitive) within a short distance
    s = re.sub(r"(?i)(otp[^\d]{0,30}?)(\b\d{6}\b)", r"\g<1>***", s)
    return s

def redact_pii(logger, log_method, event_dict):
    """
    Recursively redacts PII from the structlog event dictionary.
    """
    def _redact_value(value):
        if isinstance(value, str):
            return redact_string(value)
        elif isinstance(value, dict):
            return {k: _redact_value(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [_redact_value(v) for v in value]
        elif isinstance(value, tuple):
            return tuple(_redact_value(v) for v in value)
        return value

    for key, value in event_dict.items():
        event_dict[key] = _redact_value(value)

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
        redact_pii,
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
