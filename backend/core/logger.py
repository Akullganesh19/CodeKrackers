import logging
import re
import sys
from typing import Any, Dict

import structlog

EMAIL_REGEX = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
PHONE_REGEX = re.compile(r'(?i)\b(phone=|to\s|phone_number=|identifier=)(\+?[1-9]\d{7,14})\b')
# Ensure strict boundaries to prevent matching long IDs. Looking for 6 digit OTP.
OTP_REGEX = re.compile(r'(?i)\b(otp\s+sent.*?:\s*|otp=|code=)(\d{6})\b')
SSN_REGEX = re.compile(r'(?i)\b(ssn=|social\s+security\s+number=)(\d{3}-\d{2}-\d{4}|\d{9})\b')

SENSITIVE_KEYS = {"phone", "email", "otp", "ssn", "password", "phone_number", "identifier", "code"}

def redact_pii(logger: Any, method_name: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
    def _redact_value(v: Any) -> Any:
        if isinstance(v, str):
            v = EMAIL_REGEX.sub("[REDACTED EMAIL]", v)
            v = PHONE_REGEX.sub(lambda m: m.group(1) + "[REDACTED PHONE]", v)
            v = OTP_REGEX.sub(lambda m: m.group(1) + "[REDACTED OTP]", v)
            v = SSN_REGEX.sub(lambda m: m.group(1) + "[REDACTED SSN]", v)
            return v
        if isinstance(v, dict):
            return {k: "[REDACTED]" if isinstance(k, str) and k.lower() in SENSITIVE_KEYS else _redact_value(val) for k, val in v.items()}
        if isinstance(v, list):
            return [_redact_value(item) for item in v]
        return v

    # Process event message and kwargs
    return _redact_value(event_dict)

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
