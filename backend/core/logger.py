import logging
import sys
import re
import structlog

# Redaction patterns
# Use capturing groups to preserve context
EMAIL_REGEX = re.compile(r'([a-zA-Z0-9_.+-]{1,2})[a-zA-Z0-9_.+-]*(@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)')
IP_REGEX = re.compile(r'\b([0-9]{1,3}\.)[0-9]{1,3}\.[0-9]{1,3}(\.[0-9]{1,3})\b')
PHONE_REGEX = re.compile(r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?[0-9]{3}[-.\s]?([0-9]{4})\b')

def redact_string(text: str) -> str:
    if not isinstance(text, str):
        return text
    # j***@gmail.com
    text = EMAIL_REGEX.sub(r'\1***\2', text)
    # 123-***-4567
    text = PHONE_REGEX.sub(r'\1-***-\2', text)
    # 192.***.***.1
    text = IP_REGEX.sub(r'\1***.***\2', text)
    return text

def redact_nested(data):
    if isinstance(data, str):
        return redact_string(data)
    elif isinstance(data, dict):
        return {k: redact_nested(v) for k, v in data.items()}
    elif isinstance(data, (list, tuple)):
        return type(data)(redact_nested(v) for v in data)
    return data

def redact_structlog(logger, method_name, event_dict):
    for key, value in event_dict.items():
        event_dict[key] = redact_nested(value)
    return event_dict

class RedactFilter(logging.Filter):
    def filter(self, record):
        if isinstance(record.msg, str):
            record.msg = redact_string(record.msg)
        if hasattr(record, 'args') and record.args:
            record.args = redact_nested(record.args)
        return True

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

    for handler in logging.root.handlers:
        handler.addFilter(RedactFilter())

    processors = [
        redact_structlog,
        structlog.contextvars.merge_contextvars,
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
