import logging
import sys
import re

import structlog

EMAIL_RE = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
PHONE_RE = re.compile(r"(?:\+\d{10,15}|\b\d{10,15}\b)")
OTP_RE = re.compile(r"\b\d{6}\b")

def redact_sensitive_data(logger, method_name, event_dict):
    sensitive_keys = {'password', 'secret', 'otp'}
    for key, value in list(event_dict.items()):
        if isinstance(key, str) and any(s in key.lower() for s in sensitive_keys):
            event_dict[key] = "***"
        elif isinstance(value, str):
            def mask_email(match):
                email = match.group(0)
                parts = email.split('@')
                if len(parts) == 2 and len(parts[0]) > 0:
                    return f"{parts[0][0]}***@{parts[1]}"
                return "***@***"
            val = EMAIL_RE.sub(mask_email, value)
            val = PHONE_RE.sub("***", val)
            val = OTP_RE.sub("***", val)
            event_dict[key] = val
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
