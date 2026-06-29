import logging
import sys

import structlog

import re

EMAIL_REGEX = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b')
PHONE_REGEX = re.compile(r'(?i)(phone=|to\s+)(\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})\b')
OTP_REGEX = re.compile(r'(?i)(->\s*|otp=)(\b\d{4,6}\b)')

SENSITIVE_KEYS = {"phone", "otp", "ssn", "email", "password", "card_number", "phone_number"}

def redact_pii(logger, log_method, event_dict):
    def mask_string(text: str) -> str:
        text = EMAIL_REGEX.sub("[REDACTED EMAIL]", text)
        text = PHONE_REGEX.sub(r"\1[REDACTED PHONE]", text)
        text = OTP_REGEX.sub(r"\1[REDACTED OTP]", text)
        return text

    def traverse_and_redact(obj):
        if isinstance(obj, dict):
            new_dict = {}
            for k, v in obj.items():
                if isinstance(k, str) and k.lower() in SENSITIVE_KEYS:
                    new_dict[k] = "[REDACTED]"
                else:
                    new_dict[k] = traverse_and_redact(v)
            return new_dict
        elif isinstance(obj, list):
            return [traverse_and_redact(item) for item in obj]
        elif isinstance(obj, str):
            return mask_string(obj)
        return obj

    return traverse_and_redact(event_dict)



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
