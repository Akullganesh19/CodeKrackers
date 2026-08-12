import logging
import sys
import json
import re
from typing import Any, Dict

import structlog

# Robust regex to match emails and phone numbers (including international formats)
EMAIL_REGEX = re.compile(r"([a-zA-Z0-9_.+-]+)@([a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)")
PHONE_REGEX = re.compile(r"(?:\+?\d{1,4}[\s.-]?)?(?:\(?\d{2,5}\)?[\s.-]?)?(?:\d[\s.-]?){7,11}\d")

def redact_string(text: str) -> str:
    """Redacts emails and phone numbers from a string while preserving context."""
    def _redact_email(match):
        user, domain = match.groups()
        if len(user) > 1:
            return f"{user[0]}***@{domain}"
        return f"***@{domain}"

    def _redact_phone(match):
        val = match.group(0)
        # Exclude short numeric strings like 6-digit OTPs
        digits = re.sub(r'\D', '', val)
        if len(digits) >= 10:
            return f"[REDACTED_PHONE:{digits[-4:]}]"
        return val

    text = EMAIL_REGEX.sub(_redact_email, text)
    text = PHONE_REGEX.sub(_redact_phone, text)
    return text

class RedactingFormatter(logging.Formatter):
    """
    Standard logging formatter that applies redaction to string messages.
    Bypasses fully serialized JSON to prevent corrupting structure.
    """
    def format(self, record):
        original_msg = super().format(record)
        try:
            # If it's already a valid JSON string (e.g. from structlog),
            # don't apply string redaction as it could unquote values and break JSON.
            # Redaction for JSON is handled by `redact_dict_processor`.
            json.loads(original_msg)
            return original_msg
        except json.JSONDecodeError:
            pass
        return redact_string(original_msg)

def _redact_recursive(data: Any) -> Any:
    """Recursively redacts strings in nested dictionaries and lists."""
    if isinstance(data, str):
        return redact_string(data)
    elif isinstance(data, dict):
        return {k: _redact_recursive(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [_redact_recursive(item) for item in data]
    return data

def redact_dict_processor(logger: Any, log_method: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Structlog processor to redact sensitive data from dicts before JSON serialization."""
    for key, value in event_dict.items():
        event_dict[key] = _redact_recursive(value)
    return event_dict

def setup_logging(json_logs: bool = True, log_level: int = logging.INFO):
    """
    Configure standard logging and structlog with irreversible redaction of PII.
    """
    # Configure standard logging to route through our RedactingFormatter
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(RedactingFormatter("%(message)s"))

    # We clear existing handlers to avoid duplicates during hot reloads
    logging.root.handlers = []
    logging.basicConfig(
        handlers=[handler],
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
        redact_dict_processor, # Inject redactor before rendering
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
