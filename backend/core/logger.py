import logging
import sys

import structlog

import re

EMAIL_REGEX = re.compile(r'\b([a-zA-Z0-9._%+-])[a-zA-Z0-9._%+-]*(@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b')
PHONE_REGEX = re.compile(r'\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b')
SENSITIVE_KEYS = {"email", "phone", "phone_number", "password", "otp", "code", "identifier", "username"}

def redact_sensitive_data(logger, method_name, event_dict):
    event = str(event_dict.get("event", ""))
    event = EMAIL_REGEX.sub(r'\g<1>***\g<2>', event)

    def phone_repl(m):
        digits = re.sub(r'\D', '', m.group(0))
        if len(digits) >= 4:
            return f"***-***-{digits[-4:]}"
        return "***-***-****"

    event = PHONE_REGEX.sub(phone_repl, event)
    event = re.sub(r'(?i)(->\s*)(\d{6,8})\b', r'\g<1>[REDACTED]', event)
    event = re.sub(r'(?i)\b(otp|code)[:=\s]+(\d{6,8})\b', r'\1=[REDACTED]', event)
    event_dict["event"] = event

    for key, value in event_dict.items():
        if isinstance(key, str) and key.lower() in SENSITIVE_KEYS:
            if isinstance(value, str):
                if "@" in value:
                    event_dict[key] = EMAIL_REGEX.sub(r'\g<1>***\g<2>', value)
                elif re.match(r'^\+?[\d\s\-\(\)]+$', value) and len(re.sub(r'\D', '', value)) >= 7:
                    event_dict[key] = PHONE_REGEX.sub(phone_repl, value)
                else:
                    event_dict[key] = "[REDACTED]"
            else:
                event_dict[key] = "[REDACTED]"
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
