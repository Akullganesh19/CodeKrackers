import logging
import sys
import re

import structlog

SENSITIVE_KEYS = {"phone", "otp", "ssn", "password", "email", "address", "dob", "card_number", "phone_number"}
EMAIL_REGEX = re.compile(r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)")
PHONE_REGEX = re.compile(r"(?i)(phone=|to\s+|sender=|phone\s+)([+]?\d{10,15})")
OTP_REGEX = re.compile(r"(?i)(->\s*|otp[:=]\s*)(\d{4,6})")

def mask_email(email_str: str) -> str:
    parts = email_str.split("@")
    if len(parts) == 2:
        return f"{parts[0][0]}***@{parts[1]}"
    return "***"

def _redact_string(text: str) -> str:
    def email_repl(match):
        return mask_email(match.group(1))
    text = EMAIL_REGEX.sub(email_repl, text)

    def phone_repl(match):
        prefix = match.group(1)
        phone = match.group(2)
        masked = "*" * (len(phone) - 4) + phone[-4:] if len(phone) > 4 else "***"
        return f"{prefix}{masked}"
    text = PHONE_REGEX.sub(phone_repl, text)

    def otp_repl(match):
        prefix = match.group(1)
        return f"{prefix}***"
    text = OTP_REGEX.sub(otp_repl, text)

    return text

def redact_pii(logger, log_method, event_dict):
    def _traverse(obj):
        if isinstance(obj, dict):
            new_dict = {}
            for k, v in obj.items():
                if isinstance(k, str) and k.lower() in SENSITIVE_KEYS:
                    new_dict[k] = "[REDACTED]"
                else:
                    new_dict[k] = _traverse(v)
            return new_dict
        elif isinstance(obj, list):
            return [_traverse(item) for item in obj]
        elif isinstance(obj, str):
            return _redact_string(obj)
        else:
            return obj

    return _traverse(event_dict)

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
        redact_pii,
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
