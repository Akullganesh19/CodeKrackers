import logging
import sys
import re

import structlog

patterns = [
    (
        re.compile(r"\b([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})\b"),
        r"[REDACTED_EMAIL]",
    ),
    (re.compile(r"(->\s*)\b(\d{6})\b"), r"\g<1>[REDACTED_OTP]"),
    (
        re.compile(r"\b(code|otp)[:=]?\s*\b(\d{6})\b", re.IGNORECASE),
        r"\g<1>=[REDACTED_OTP]",
    ),
    (
        re.compile(
            r"(?i)(phone=|sender=|to |for |identifier=|\+)(?<!\d)(\d{10,15})(?!\d)"
        ),
        r"\g<1>[REDACTED_PHONE]",
    ),
]


def redact_string(s: str) -> str:
    for pattern, repl in patterns:
        s = pattern.sub(repl, s)
    return s


def redact_pii(logger, method_name, event_dict):
    """
    structlog processor to recursively redact PII from log events.
    """

    def redact_recursive(obj):
        if isinstance(obj, str):
            return redact_string(obj)
        elif isinstance(obj, dict):
            return {k: redact_recursive(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [redact_recursive(v) for v in obj]
        elif isinstance(obj, tuple):
            return tuple(redact_recursive(v) for v in obj)
        return obj

    for key, value in event_dict.items():
        event_dict[key] = redact_recursive(value)

    return event_dict


def setup_logging(json_logs: bool = True, log_level: int = logging.INFO):
    """
    Configure standard logging and structlog.
    """

    # Processors for both structlog native logs and standard logging
    shared_processors = [
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        redact_pii,  # Added redaction
    ]

    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=shared_processors,
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            (
                structlog.processors.JSONRenderer()
                if json_logs
                else structlog.dev.ConsoleRenderer()
            ),
        ],
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(log_level)


def get_logger(name: str):
    """
    Returns a structlog configured logger.
    """
    return structlog.get_logger(name)
