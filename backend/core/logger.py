import logging
import sys

import structlog

from backend.core.redaction import redact_pii


def _redact_dict(d: dict) -> dict:
    """Recursively redact strings inside a dictionary."""
    redacted = {}
    for k, v in d.items():
        if isinstance(v, str):
            redacted[k] = redact_pii(v)
        elif isinstance(v, dict):
            redacted[k] = _redact_dict(v)
        elif isinstance(v, list):
            redacted[k] = _redact_list(v)
        else:
            redacted[k] = v
    return redacted


def _redact_list(lst: list) -> list:
    """Recursively redact strings inside a list."""
    redacted = []
    for v in lst:
        if isinstance(v, str):
            redacted.append(redact_pii(v))
        elif isinstance(v, dict):
            redacted.append(_redact_dict(v))
        elif isinstance(v, list):
            redacted.append(_redact_list(v))
        else:
            redacted.append(v)
    return redacted


def pii_redactor_processor(logger, log_method, event_dict):
    """
    Structlog processor that redacts PII from event messages and values.
    """
    for key, value in event_dict.items():
        if isinstance(value, str):
            event_dict[key] = redact_pii(value)
        elif isinstance(value, dict):
            event_dict[key] = _redact_dict(value)
        elif isinstance(value, list) or isinstance(value, tuple):
            event_dict[key] = type(value)(_redact_list(value))

    # Redact positional arguments if they exist
    if "positional_args" in event_dict:
        redacted_args = []
        for arg in event_dict["positional_args"]:
            if isinstance(arg, str):
                redacted_args.append(redact_pii(arg))
            elif isinstance(arg, dict):
                redacted_args.append(_redact_dict(arg))
            elif isinstance(arg, list) or isinstance(arg, tuple):
                redacted_args.append(type(arg)(_redact_list(arg)))
            else:
                redacted_args.append(arg)
        event_dict["positional_args"] = tuple(redacted_args)

    return event_dict


class PIIRedactingFormatter(logging.Formatter):
    """
    Formatter to redact PII from standard library log messages
    before they are processed or emitted.
    """

    def format(self, record):
        original_msg = super().format(record)
        return redact_pii(original_msg)


def setup_logging(json_logs: bool = True, log_level: int = logging.INFO):
    """
    Configure standard logging and structlog with PII redaction.
    """
    # Configure standard logging to route through structlog
    handler = logging.StreamHandler(sys.stdout)
    formatter = PIIRedactingFormatter(fmt="%(message)s")
    handler.setFormatter(formatter)

    logging.root.handlers = [handler]
    logging.root.setLevel(log_level)

    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        pii_redactor_processor,  # Add the PII redactor processor
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
