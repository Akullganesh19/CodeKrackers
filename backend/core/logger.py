import logging
import sys

import structlog

from backend.core.redaction import redact_string, redact_dict

class RedactingFormatter(logging.Formatter):
    def format(self, record):
        msg = super().format(record)
        return redact_string(msg)

def redact_structlog_processor(logger, method_name, event_dict):
    event_dict = redact_dict(event_dict)
    if "event" in event_dict and isinstance(event_dict["event"], str):
        event_dict["event"] = redact_string(event_dict["event"])
    if "exc_info" in event_dict and isinstance(event_dict["exc_info"], str):
        event_dict["exc_info"] = redact_string(event_dict["exc_info"])
    if "stack_info" in event_dict and isinstance(event_dict["stack_info"], str):
        event_dict["stack_info"] = redact_string(event_dict["stack_info"])
    return event_dict


def setup_logging(json_logs: bool = True, log_level: int = logging.INFO):
    """
    Configure standard logging and structlog.
    """
    # Configure standard logging to route through structlog
    if logging.root.handlers:
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)

    formatter = RedactingFormatter("%(message)s")
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    logging.root.addHandler(handler)
    logging.root.setLevel(log_level)

    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        redact_structlog_processor,
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
