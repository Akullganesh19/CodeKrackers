import logging
import sys

import structlog
import re
from typing import Any, Dict

def redact_sensitive_data(logger, method_name, event_dict):
    sensitive_keys = ['password', 'secret', 'otp', 'token', 'access_token', 'refresh_token']
    for key in sensitive_keys:
        if key in event_dict:
            event_dict[key] = '***'

    if 'event' in event_dict and isinstance(event_dict['event'], str):
        event_str = event_dict['event']

        # Email masking
        event_str = re.sub(
            r'\b([a-zA-Z0-9])[a-zA-Z0-9_.+-]*(@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)\b',
            r'\1***\2',
            event_str
        )

        # Phone masking
        event_str = re.sub(
            r'\b((?:\+?\d{1,3}[\s-]?)?\d{2})\d{5}(\d{3})\b',
            r'\1***\2',
            event_str
        )

        # OTP masking
        event_str = re.sub(
            r'\bOTP(?:\s+for\s+[^:]+)?\s*[:\-]?\s*(\d{4,6})\b',
            r'OTP: ***',
            event_str,
            flags=re.IGNORECASE
        )

        event_dict['event'] = event_str

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
        redact_sensitive_data,
        structlog.stdlib.PositionalArgumentsFormatter(),
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
