import logging
import sys
import re

import structlog

def redact_sensitive_data(logger, method_name, event_dict):
    SENSITIVE_KEYS = {"password", "secret", "otp", "token", "ssn", "card", "email", "phone"}

    for key in list(event_dict.keys()):
        if isinstance(key, str):
            key_lower = key.lower()
            if any(s_key in key_lower for s_key in SENSITIVE_KEYS):
                val = event_dict[key]
                if isinstance(val, str) and "@" in val and key_lower == "email":
                    parts = val.split('@')
                    if len(parts) == 2 and len(parts[0]) > 0:
                        event_dict[key] = f"{parts[0][0]}***@{parts[1]}"
                    else:
                        event_dict[key] = "[REDACTED]"
                else:
                    event_dict[key] = "[REDACTED]"

    event = event_dict.get("event")
    if isinstance(event, str):
        def mask_email(match):
            email = match.group(0)
            parts = email.split('@')
            if len(parts) == 2 and len(parts[0]) > 0:
                return f"{parts[0][0]}***@{parts[1]}"
            return "***@***"
        event = re.sub(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", mask_email, event)

        event = re.sub(r"\b\d{6}\b", "[REDACTED_OTP]", event)

        def mask_phone(match):
            phone = match.group(0)
            return f"{phone[:3]}***{phone[-2:]}"

        event = re.sub(r"(?:\+?\d{1,3}[- ]?)?\(?\d{3}\)?[- ]?\d{3}[- ]?\d{4}\b", mask_phone, event)

        event_dict["event"] = event

    return event_dict

def setup_logging(json_logs: bool = True, log_level: int = logging.INFO):
    """
    Configure standard logging and structlog.
    """
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
