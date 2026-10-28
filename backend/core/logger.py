import logging
import sys

import structlog

import re

def redact_sensitive_data(logger, log_method, event_dict):
    sensitive_keys = {"password", "secret", "otp", "token", "access_token"}
    for key in sensitive_keys:
        if key in event_dict:
            event_dict[key] = "***REDACTED***"

    def mask_string(s):
        if not isinstance(s, str):
            return s
        s = re.sub(r'\b([a-zA-Z0-9])[a-zA-Z0-9._%+-]*(@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b', r'\1***\2', s)
        s = re.sub(r'(?<!\d)(?:\+?\d{1,3}[\s.-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?(\d{4})(?!\d)', r'***-***-\1', s)
        return s

    for key in ["email", "phone", "phone_number", "identifier"]:
        if key in event_dict:
            event_dict[key] = mask_string(event_dict[key])

    if "event" in event_dict and isinstance(event_dict["event"], str):
        event_dict["event"] = mask_string(event_dict["event"])

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
