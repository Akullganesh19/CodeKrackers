import logging
import sys
import re

import structlog

EMAIL_REGEX = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b')
PHONE_PATTERN = re.compile(r'(?P<prefix>\bphone=|\bto |\bfor |\bsender=)(?P<phone>\+?\d{7,15})\b')
OTP_PATTERN = re.compile(r'(?P<prefix>-> |\bcode: |\bOTP:? |\bCode: )(?P<otp>\d{6})\b')

# Fields that should be fully redacted if passed as structured kwargs
SENSITIVE_KWARGS = {"phone", "phone_number", "sender", "to", "otp", "code", "password", "ssn"}

def redact_email(match):
    email = match.group(0)
    parts = email.split('@')
    if len(parts) == 2:
        name, domain = parts
        if len(name) > 1:
            name = name[0] + "***"
        else:
            name = "***"
        return f"{name}@{domain}"
    return email

def redact_string(text: str) -> str:
    text = EMAIL_REGEX.sub(redact_email, text)
    text = PHONE_PATTERN.sub(r'\g<prefix>[REDACTED]', text)
    text = OTP_PATTERN.sub(r'\g<prefix>[REDACTED]', text)
    return text

def redact_pii(logger, log_method, event_dict):
    """
    Structlog processor to redact PII (emails, phone numbers, OTPs) from log messages and arguments.
    """
    for key, value in list(event_dict.items()):
        # Redact known sensitive kwarg keys entirely
        if key.lower() in SENSITIVE_KWARGS:
            event_dict[key] = "[REDACTED]"
            continue
        # Partially redact emails in email keys
        if key.lower() in {"email", "email_address"}:
            if isinstance(value, str):
                event_dict[key] = redact_email(re.match(r'.*', value)) if '@' in value else "[REDACTED]"
            continue

        # Otherwise apply general string redaction
        if isinstance(value, str):
            event_dict[key] = redact_string(value)
        elif isinstance(value, (list, tuple)):
            new_val = []
            for item in value:
                if isinstance(item, str):
                    new_val.append(redact_string(item))
                else:
                    new_val.append(item)
            event_dict[key] = type(value)(new_val)
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
