import logging
import sys
import re

import structlog

EMAIL_REGEX = re.compile(r"\b([A-Za-z0-9._%+-]+)(@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})\b")
PHONE_REGEX = re.compile(r"(?i)(phone=|to\s+)(\+?\b\d{7,15}\b)")
OTP_REGEX = re.compile(r"(?i)(->\s*|otp\s+)(\b\d{4,8}\b)")


def _redact_string(text: str) -> str:
    def redact_email(m):
        name, domain = m.group(1), m.group(2)
        masked = name[0] + "***" if len(name) > 1 else "***"
        return f"{masked}{domain}"

    text = EMAIL_REGEX.sub(redact_email, text)

    def redact_phone(m):
        return f"{m.group(1)}[REDACTED]"

    text = PHONE_REGEX.sub(redact_phone, text)

    def redact_otp(m):
        return f"{m.group(1)}[REDACTED]"

    text = OTP_REGEX.sub(redact_otp, text)
    return text


SENSITIVE_KEYS = {"phone", "otp", "ssn", "password", "card_number", "email"}


def redact_pii(logger, method_name, event_dict):
    def walk_and_redact(obj):
        if isinstance(obj, dict):
            new_dict = {}
            for k, v in obj.items():
                if isinstance(k, str) and k.lower() in SENSITIVE_KEYS:
                    if isinstance(v, str) and "@" in v and k.lower() == "email":
                        redacted = _redact_string(v)
                        new_dict[k] = redacted if redacted != v else "[REDACTED]"
                    else:
                        new_dict[k] = "[REDACTED]"
                else:
                    new_dict[k] = walk_and_redact(v)
            return new_dict
        elif isinstance(obj, (list, tuple, set)):
            return [walk_and_redact(item) for item in obj]
        elif isinstance(obj, str):
            return _redact_string(obj)
        else:
            return obj

    return walk_and_redact(event_dict)


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
