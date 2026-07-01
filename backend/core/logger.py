import logging
import re
import sys
from typing import Any, Dict

import structlog

SENSITIVE_KEYS = {"phone", "email", "otp", "ssn", "password", "card_number"}

PHONE_PATTERN = re.compile(r"(?i)\b(phone=|to\s+)(\+?\d{7,15})\b")
EMAIL_PATTERN = re.compile(r"(?i)\b(email=)([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)\b")
OTP_SSN_PATTERN = re.compile(r"(?i)\b(otp=|ssn=)(\d{4,8}|\d{3}-\d{2}-\d{4})\b")

def redact_string(text: str) -> str:
    text = PHONE_PATTERN.sub(r"\1[REDACTED]", text)
    text = EMAIL_PATTERN.sub(r"\1[REDACTED]", text)
    text = OTP_SSN_PATTERN.sub(r"\1[REDACTED]", text)
    return text

def redact_pii(logger: Any, method_name: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
    def _traverse_and_redact(obj: Any) -> Any:
        if isinstance(obj, dict):
            new_dict = {}
            for k, v in obj.items():
                if isinstance(k, str) and k.lower() in SENSITIVE_KEYS:
                    new_dict[k] = "[REDACTED]"
                else:
                    new_dict[k] = _traverse_and_redact(v)
            return new_dict
        elif isinstance(obj, list):
            return [_traverse_and_redact(item) for item in obj]
        elif isinstance(obj, tuple):
            return tuple(_traverse_and_redact(item) for item in obj)
        elif isinstance(obj, set):
            return {_traverse_and_redact(item) for item in obj}
        elif isinstance(obj, str):
            return redact_string(obj)
        return obj

    return _traverse_and_redact(event_dict)

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
