import logging
import sys

import structlog
import re

def redact_string(text: str) -> str:
    if not isinstance(text, str):
        return text
    # Redact email
    text = re.sub(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', '[REDACTED_EMAIL]', text)

    # Redact phone (e.g., matching 'phone', 'to', etc. but as per the instructions, just rely on context or generic redaction cautiously)
    # The instructions specifically said: "PII regexes use context boundaries (e.g., matching 'phone=' or 'to ' prefixes) to prevent accidental redaction of IDs and timestamps."
    text = re.sub(r'(phone(?:[\s=:]*)|to\s+|for\s+)(\+?\d{10,15})\b', r'\1[REDACTED_PHONE]', text, flags=re.IGNORECASE)

    # Redact OTPs
    text = re.sub(r'(->\s*|code(?:[\s=:]*)|otp(?:[\s=:]*))(\d{4,8})\b', r'\1[REDACTED_OTP]', text, flags=re.IGNORECASE)

    return text

def redact_pii(logger, log_method, event_dict):
    def redact_recursive(key, obj):
        if isinstance(obj, str):
            # If the key itself indicates PII, we might want to redact the whole string if it's a value, but we also rely on string replacement.
            # But string replacement only works if the context is inside the string. If it's a kwarg like phone="+1234567890", the context is the key!
            if key is not None and isinstance(key, str):
                key_lower = key.lower()
                if 'email' in key_lower:
                    return '[REDACTED_EMAIL]'
                if 'phone' in key_lower:
                    return '[REDACTED_PHONE]'
                if 'code' in key_lower or 'otp' in key_lower:
                    return '[REDACTED_OTP]'
            return redact_string(obj)
        elif isinstance(obj, dict):
            return {k: redact_recursive(k, v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [redact_recursive(key, item) for item in obj]
        return obj

    return redact_recursive(None, event_dict)

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
        redact_pii,
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
