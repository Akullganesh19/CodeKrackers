import logging
import re
import sys

import structlog

_EMAIL_PATTERN = re.compile(
    r"([a-zA-Z0-9])[a-zA-Z0-9_.+-]*(@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)"
)
_PHONE_PATTERN = re.compile(
    r"(?P<prefix>phone=|to\s+)(?P<number>\+?\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4})",
    re.IGNORECASE,
)


def _redact_email_match(match):
    return f"{match.group(1)}***{match.group(2)}"


def _mask_phone_match(match):
    prefix = match.group("prefix") or ""
    number = match.group("number")
    if len(number) > 6:
        masked_number = number[:4] + "***" + number[-2:]
    else:
        masked_number = "***"
    return f"{prefix}{masked_number}"


def redact_pii_processor(logger, log_method, event_dict):
    sensitive_keys = {
        "email",
        "phone",
        "password",
        "ssn",
        "identifier",
        "otp_code",
        "phone_number",
    }

    for key, value in list(event_dict.items()):
        if isinstance(key, str) and key.lower() in sensitive_keys:
            if isinstance(value, str):
                if "@" in value and _EMAIL_PATTERN.search(value):
                    event_dict[key] = _EMAIL_PATTERN.sub(_redact_email_match, value)
                else:
                    event_dict[key] = "***"

    event_str = event_dict.get("event")
    if isinstance(event_str, str):
        event_str = _EMAIL_PATTERN.sub(_redact_email_match, event_str)
        event_str = _PHONE_PATTERN.sub(_mask_phone_match, event_str)
        event_dict["event"] = event_str

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
        redact_pii_processor,
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
