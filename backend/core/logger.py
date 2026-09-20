import logging
import sys

import structlog
import re

EMAIL_REGEX = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
PHONE_REGEX = re.compile(r'\B\+[1-9]\d{6,14}\b')

def redact_email(match):
    email = match.group(0)
    parts = email.split('@')
    if len(parts[0]) > 1:
        return f"{parts[0][0]}***@{parts[1]}"
    return f"***@{parts[1]}"

def redact_phone(match):
    phone = match.group(0)
    return f"{phone[:4]}***{phone[-2:]}"

def redact_string(text: str) -> str:
    if not isinstance(text, str):
        return text
    text = EMAIL_REGEX.sub(redact_email, text)
    text = PHONE_REGEX.sub(redact_phone, text)
    text = re.sub(r'(?i)(otp|code)[^\d]*(\b\d{6}\b)', r'\1: [REDACTED_OTP]', text)
    text = re.sub(r'(->)\s*(\b\d{6}\b)', r'\1 [REDACTED_OTP]', text)
    return text

class RedactingFilter(logging.Filter):
    def filter(self, record):
        if isinstance(record.msg, str):
            record.msg = redact_string(record.msg)
        if isinstance(record.args, tuple):
            new_args = tuple(
                redact_string(arg) if isinstance(arg, str) else arg
                for arg in record.args
            )
            record.args = new_args
        elif isinstance(record.args, dict):
            new_args = {
                k: (redact_string(v) if isinstance(v, str) else v)
                for k, v in record.args.items()
            }
            record.args = new_args
        return True

def redact_recursive(data):
    if isinstance(data, str):
        return redact_string(data)
    elif isinstance(data, dict):
        return {k: redact_recursive(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [redact_recursive(v) for v in data]
    elif isinstance(data, tuple):
        return tuple(redact_recursive(v) for v in data)
    return data

def redact_structlog(logger, log_method, event_dict):
    for k, v in event_dict.items():
        event_dict[k] = redact_recursive(v)
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

    root_logger = logging.getLogger()
    redacting_filter = RedactingFilter()
    for handler in root_logger.handlers:
        handler.addFilter(redacting_filter)

    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        redact_structlog,
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
