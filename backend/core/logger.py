import logging
import sys

import structlog

import re

def redact_pii(logger, log_method, event_dict):
    """
    Custom structlog processor to redact PII (emails, phones, OTPs, etc.)
    """
    def redact_string(value: str) -> str:
        if not isinstance(value, str):
            return value
        # Redact email
        value = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[REDACTED_EMAIL]', value)
        # Redact phone (with context boundaries to avoid redacting random IDs)
        value = re.sub(r'(phone=|to |\+|source_number=)[0-9]{10,15}\b', r'\g<1>[REDACTED_PHONE]', value)
        # Redact OTP
        value = re.sub(r'\b(otp|code|OTP)[:=]\s*[0-9]{4,6}\b', r'\g<1>=[REDACTED_OTP]', value)
        # Redact passwords in kwargs
        value = re.sub(r'\bpassword=.*', 'password=[REDACTED]', value)
        return value

    def traverse_and_redact(data):
        if isinstance(data, dict):
            for k, v in data.items():
                if isinstance(k, str) and k.lower() in ('phone', 'phone_number', 'otp', 'code', 'email', 'password', 'ssn', 'source_number'):
                    data[k] = '[REDACTED]'
                else:
                    data[k] = traverse_and_redact(v)
            return data
        elif isinstance(data, list):
            return [traverse_and_redact(item) for item in data]
        elif isinstance(data, str):
            return redact_string(data)
        return data

    event_dict = traverse_and_redact(event_dict)

    # Also explicitly redact the main event message string
    if 'event' in event_dict and isinstance(event_dict['event'], str):
         event_dict['event'] = redact_string(event_dict['event'])

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
