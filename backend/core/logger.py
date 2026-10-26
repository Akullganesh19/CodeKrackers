import logging
import sys
import re
import structlog
from typing import Any

# Compile regex patterns once for performance
_EMAIL_PATTERN = re.compile(r'\b([a-zA-Z0-9_.+-])[a-zA-Z0-9_.+-]*(@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)\b')
_PHONE_PATTERN = re.compile(r'\+?\d{1,3}?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?(\d{4})\b')
_OTP_PATTERN = re.compile(r'(?i)(otp.*?)(?:->|:)\s*(\d{6})\b')
_PASSWORD_PATTERN = re.compile(r'(?i)(password|pwd|secret)\s*(=|:)\s*[^\s]+')

_SENSITIVE_KEYS = {'password', 'pwd', 'secret', 'otp', 'token', 'access_token'}

def redact_sensitive_data(logger, log_method, event_dict: dict) -> dict:
    """
    Redact PII (email, phone numbers, passwords, OTPs) from structlog event dictionary.
    Handles nested dictionaries/lists and redacts entirely based on sensitive keys.
    """
    def _redact_string(val: str) -> str:
        val = _EMAIL_PATTERN.sub(r'\g<1>***\g<2>', val)
        val = _PHONE_PATTERN.sub(r'***-***-\g<1>', val)
        val = _OTP_PATTERN.sub(r'\g<1>***', val)
        val = _PASSWORD_PATTERN.sub(r'\g<1>\g<2>***', val)
        return val

    def _traverse_and_redact(data: Any, key_name: str = "") -> Any:
        # If the key itself is sensitive, redact the whole value
        if any(sensitive in key_name.lower() for sensitive in _SENSITIVE_KEYS):
            return "***"

        if isinstance(data, dict):
            return {k: _traverse_and_redact(v, k) for k, v in data.items()}
        elif isinstance(data, (list, tuple)):
            return type(data)(_traverse_and_redact(item, key_name) for item in data)
        elif isinstance(data, str):
            return _redact_string(data)
        else:
            return data

    # Traverse all kwargs in the event dictionary
    redacted_event = {}
    for key, value in event_dict.items():
        if key == "event" and isinstance(value, str):
            redacted_event[key] = _redact_string(value)
        elif key == "positional_args" and isinstance(value, tuple):
            redacted_event[key] = tuple(_redact_string(arg) if isinstance(arg, str) else arg for arg in value)
        else:
            redacted_event[key] = _traverse_and_redact(value, key)

    return redacted_event

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
