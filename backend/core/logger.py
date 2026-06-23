import logging
import sys
import re

import structlog

def redact_string(text: str) -> str:
    # Emails
    text = re.sub(r'\b[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+\b', '[REDACTED_EMAIL]', text)

    # Phone numbers
    text = re.sub(r'(?i)(phone=)\+?[0-9\s-]{7,15}\b', r'\g<1>[REDACTED_PHONE]', text)
    text = re.sub(r'(?i)(to\s+)\+?[0-9\s-]{7,15}\b', r'\g<1>[REDACTED_PHONE]', text)
    text = re.sub(r'(?i)(from\s+)\+?[0-9\s-]{7,15}\b', r'\g<1>[REDACTED_PHONE]', text)
    text = re.sub(r'(?i)(for\s+)\+?[0-9\s-]{7,15}\b', r'\g<1>[REDACTED_PHONE]', text)

    # OTPs
    text = re.sub(r'(?i)(->\s*)\d{6}\b', r'\g<1>[REDACTED_OTP]', text)
    text = re.sub(r'(?i)(otp[:\s]*)\d{6}\b', r'\g<1>[REDACTED_OTP]', text)
    text = re.sub(r'(?i)(:\s*)\d{6}\b', r'\g<1>[REDACTED_OTP]', text)

    return text

def redact_pii(logger, log_method, event_dict):
    """
    Recursively redacts PII from the event dict.
    """
    def redact_recursive(obj):
        if isinstance(obj, str):
            return redact_string(obj)
        elif isinstance(obj, dict):
            res = {}
            for k, v in obj.items():
                if isinstance(v, str) and k in ["phone", "email", "phone_number"]:
                    if k in ["phone", "phone_number"]:
                        res[k] = "[REDACTED_PHONE]"
                    else:
                        res[k] = "[REDACTED_EMAIL]"
                else:
                    res[k] = redact_recursive(v)
            return res
        elif isinstance(obj, list):
            return [redact_recursive(v) for v in obj]
        return obj

    for key, value in event_dict.items():
        event_dict[key] = redact_recursive(value)

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
