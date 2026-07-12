import logging
import sys

import structlog

from backend.core.redaction import redact_string

class RedactingFormatter(logging.Formatter):
    """
    Custom formatter that redacts PII from the log message before outputting.
    """
    def format(self, record: logging.LogRecord) -> str:
        # Format the record into a string first to avoid altering the original object
        original_message = super().format(record)
        return redact_string(original_message)

def redact_structlog(logger: logging.Logger, log_method: str, event_dict: dict) -> dict:
    """
    Structlog processor to recursively redact PII from all string values in the event dictionary.
    """
    def _redact(obj):
        if isinstance(obj, str):
            return redact_string(obj)
        elif isinstance(obj, dict):
            return {k: _redact(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [_redact(i) for i in obj]
        return obj

    for key, value in event_dict.items():
        event_dict[key] = _redact(value)

    return event_dict

def setup_logging(json_logs: bool = True, log_level: int = logging.INFO):
    """
    Configure standard logging and structlog.
    """

    formatter = RedactingFormatter("%(message)s")
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    # Configure standard logging to route through structlog and use redacting formatter
    logging.basicConfig(
        level=log_level,
        handlers=[handler],
        force=True
    )

    processors = [
        structlog.contextvars.merge_contextvars,
        redact_structlog,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
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
