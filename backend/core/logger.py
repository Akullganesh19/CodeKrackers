import logging
import sys

import structlog
from backend.core.redaction import redact_string

class PIIRedactingFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        # Save original args and msg to avoid mutation
        # Format the original message into a string first
        original_msg = super().format(record)
        return redact_string(original_msg)

def redact_processor(logger, log_method, event_dict):
    for k, v in event_dict.items():
        if isinstance(v, str):
            event_dict[k] = redact_string(v)
    return event_dict


def setup_logging(json_logs: bool = True, log_level: int = logging.INFO):
    """
    Configure standard logging and structlog.
    """

    # Configure standard logging to route through structlog
    formatter = PIIRedactingFormatter("%(message)s")
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    logging.basicConfig(
        level=log_level,
        handlers=[handler]
    )


    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        redact_processor,
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
