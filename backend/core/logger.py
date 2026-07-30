import logging
import sys
import re
import json
from typing import Any, Dict

import structlog

# Regex patterns for string redaction
# Phone requiring formatting to avoid numeric IDs / timestamps
PHONE_REGEX = re.compile(r'(?:\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}')
# Context-aware OTP/code matching up to 50 characters between "otp/code" and the 6 digits
OTP_REGEX = re.compile(r'(?i)(\b(?:otp|code)\b.{0,50}?)(\b\d{6}\b)')
# Email regex
EMAIL_REGEX = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')

SENSITIVE_KEYS = {"otp", "password", "phone", "ssn", "email", "email_address", "phone_number"}

def redact_string(text: str) -> str:
    if not isinstance(text, str):
        return text
    text = EMAIL_REGEX.sub("[EMAIL REDACTED]", text)
    text = OTP_REGEX.sub(r'\1[OTP REDACTED]', text)
    text = PHONE_REGEX.sub("[PHONE REDACTED]", text)
    return text

class RedactingFormatter(logging.Formatter):
    def format(self, record):
        original_msg = super().format(record)

        # If the output is a JSON string (likely from structlog JSONRenderer),
        # we must still redact it safely. Standard logger strings that happen
        # to be JSON shouldn't bypass redaction. If it's valid JSON, we parse it,
        # apply dictionary redaction, and re-serialize.
        if original_msg.strip().startswith('{') and original_msg.strip().endswith('}'):
            try:
                # Attempt to parse
                parsed = json.loads(original_msg)

                # In case structlog already redacted it, applying it again is harmless.
                # In case it's a raw standard log that is JSON, it gets redacted safely.
                redact_structlog_dict(None, None, parsed)

                return json.dumps(parsed)
            except json.JSONDecodeError:
                pass
        elif isinstance(original_msg, str):
            return redact_string(original_msg)

        return redact_string(original_msg)

def redact_structlog_dict(logger: logging.Logger, name: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
    # 1. Redact values by exact key name
    for key in list(event_dict.keys()):
        key_lower = key.lower()
        if any(sensitive_key == key_lower or sensitive_key in key_lower.split('_') for sensitive_key in SENSITIVE_KEYS):
            if event_dict[key] is not None:
                event_dict[key] = "[REDACTED]"

    # 2. Redact string content in all remaining string values
    for key, value in event_dict.items():
        if isinstance(value, str):
            event_dict[key] = redact_string(value)

    return event_dict

def setup_logging(json_logs: bool = True, log_level: int = logging.INFO):
    """
    Configure standard logging and structlog.
    """
    # Explicitly clear existing root handlers
    logging.root.handlers.clear()

    # Configure standard logging with RedactingFormatter
    handler = logging.StreamHandler(sys.stdout)
    formatter = RedactingFormatter("%(message)s")
    handler.setFormatter(formatter)
    logging.root.addHandler(handler)
    logging.root.setLevel(log_level)

    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        redact_structlog_dict,
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
