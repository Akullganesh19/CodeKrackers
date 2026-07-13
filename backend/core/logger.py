import logging
import sys

import structlog


def setup_logging(json_logs: bool = True, log_level: int = logging.INFO):
    """
    Configure standard logging and structlog.
    """
    from backend.core.redaction import redact_data, redact_string

    class RedactingFormatter(logging.Formatter):
        def format(self, record):
            original_msg = super().format(record)
            return redact_string(original_msg)

    # Configure standard logging to route through structlog with redaction
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(RedactingFormatter("%(message)s"))
    logging.basicConfig(
        handlers=[handler],
        level=log_level,
    )

    def structlog_redactor(logger, log_method, event_dict):
        return redact_data(event_dict)

    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog_redactor,
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
