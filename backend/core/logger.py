import logging
import sys

import structlog

import re

EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
PHONE_PATTERN = re.compile(r"\B\+[1-9]\d{6,14}\b")

def _redact_text(text: str) -> str:
    if not isinstance(text, str):
        return text

    def repl_email(m):
        e = m.group(0)
        try:
            user, domain = e.split('@', 1)
            if len(user) > 1:
                return f"{user[0]}***@{domain}"
            return f"***@{domain}"
        except ValueError:
            return "***"

    text = EMAIL_PATTERN.sub(repl_email, text)

    def repl_phone(m):
        p = m.group(0)
        return f"{p[:3]}***{p[-2:]}" if len(p) > 5 else "***"

    text = PHONE_PATTERN.sub(repl_phone, text)

    def repl_otp(m):
        return m.group(1) + "***"

    text = re.sub(r"(?i)(OTP(?:[^\d]*?))(\d{6})\b", repl_otp, text)

    return text

class PIIRedactionFilter(logging.Filter):
    def filter(self, record):
        if isinstance(record.msg, str):
            record.msg = _redact_text(record.msg)

        if isinstance(record.args, dict):
            new_args = {}
            for k, v in record.args.items():
                if isinstance(v, str):
                    new_args[k] = _redact_text(v)
                else:
                    new_args[k] = v
            record.args = new_args
        elif isinstance(record.args, tuple):
            new_args = []
            for v in record.args:
                if isinstance(v, str):
                    new_args.append(_redact_text(v))
                else:
                    new_args.append(v)
            record.args = tuple(new_args)

        return True

def redact_structlog_processor(logger, log_method, event_dict):
    def _redact_value(val):
        if isinstance(val, str):
            return _redact_text(val)
        elif isinstance(val, dict):
            return {k: _redact_value(v) for k, v in val.items()}
        elif isinstance(val, (list, tuple)):
            return type(val)(_redact_value(v) for v in val)
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

    # Add redaction filter to root logger
    logging.getLogger().addFilter(PIIRedactionFilter())

    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        redact_structlog_processor,
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
