import logging
import sys
import re

def mask_email_phone(text):
    if not isinstance(text, str):
        return text

    # Redact email
    def repl_email(m):
        first = m.group(1)
        domain = m.group(2)
        return f"{first}***@{domain}"

    text = re.sub(r'\b([a-zA-Z0-9])[a-zA-Z0-9._%+-]*@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b', repl_email, text)

    # Redact phone
    def repl_phone(m):
        s = m.group(0)
        digits = re.sub(r'\D', '', s)
        if len(digits) >= 10:
            return "***-***-" + digits[-4:]
        return s

    text = re.sub(r'\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b', repl_phone, text)

    return text

def redact_nested_pii(data):
    if isinstance(data, str):
        return mask_email_phone(data)
    elif isinstance(data, dict):
        return {k: redact_nested_pii(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [redact_nested_pii(v) for v in data]
    elif isinstance(data, tuple):
        return tuple(redact_nested_pii(v) for v in data)
    else:
        return data

def redact_pii_processor(logger, log_method, event_dict):
    return redact_nested_pii(event_dict)

class PIIFilter(logging.Filter):
    def filter(self, record):
        if isinstance(record.msg, str):
            record.msg = mask_email_phone(record.msg)

        if record.args:
            record.args = redact_nested_pii(record.args)

        return True


import structlog

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
        handler.addFilter(PIIFilter())

    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        redact_pii_processor,
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
