import logging
import re
import sys

import structlog


def mask_email(match):
    email = match.group(0)
    if "@" not in email:
        return email
    user, domain = email.split("@", 1)
    if len(user) > 2:
        return f"{user[0]}***{user[-1]}@{domain}"
    return f"***@{domain}"


def mask_phone(match):
    phone = match.group(0)
    digits_only = re.sub(r"\D", "", phone)
    if len(digits_only) >= 4:
        return f"***-***-{digits_only[-4:]}"
    return "[REDACTED PHONE]"


def mask_otp(match):
    return "[REDACTED OTP]"


SENSITIVE_PATTERNS = [
    (re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"), mask_email),
    (
        re.compile(r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"),
        mask_phone,
    ),
    (re.compile(r"(?<=->\s)\d{6}\b"), mask_otp),
]


class RedactingFilter(logging.Filter):  # noqa: C901
    def filter(self, record):  # noqa: C901
        if isinstance(record.msg, str):
            for pattern, replacement in SENSITIVE_PATTERNS:
                record.msg = pattern.sub(replacement, record.msg)

        if record.args:
            if isinstance(record.args, dict):
                new_args = {}
                for k, v in record.args.items():
                    if isinstance(v, str):
                        for pattern, replacement in SENSITIVE_PATTERNS:
                            v = pattern.sub(replacement, v)
                    new_args[k] = v
                record.args = new_args
            elif isinstance(record.args, tuple) or isinstance(record.args, list):
                new_args = []
                for v in record.args:
                    if isinstance(v, str):
                        for pattern, replacement in SENSITIVE_PATTERNS:
                            v = pattern.sub(replacement, v)
                    new_args.append(v)
                record.args = tuple(new_args)
        return True


def redact_structlog_event(logger, log_method, event_dict):
    def _redact_value(val):
        if isinstance(val, str):
            for pattern, replacement in SENSITIVE_PATTERNS:
                val = pattern.sub(replacement, val)
            return val
        elif isinstance(val, dict):
            return {k: _redact_value(v) for k, v in val.items()}
        elif isinstance(val, list):
            return [_redact_value(v) for v in val]
        elif isinstance(val, tuple):
            return tuple(_redact_value(v) for v in val)
        return val

    new_event_dict = {}
    for k, v in event_dict.items():
        new_event_dict[k] = _redact_value(v)
    return new_event_dict


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

    redaction_filter = RedactingFilter()
    for handler in logging.root.handlers:
        handler.addFilter(redaction_filter)

    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        redact_structlog_event,
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
