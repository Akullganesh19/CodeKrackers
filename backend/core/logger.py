import logging
import sys
import re

import structlog

class PIIRedactor:
    EMAIL_RE = re.compile(r'([a-zA-Z0-9_.+-]+)@([a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)')

    @classmethod
    def redact_email(cls, match):
        user, domain = match.groups()
        redacted_user = user[0] + "***" if len(user) > 0 else "***"
        return f"{redacted_user}@{domain}"

    @classmethod
    def redact_string(cls, text: str) -> str:
        if not isinstance(text, str):
            return text

        text = cls.EMAIL_RE.sub(cls.redact_email, text)

        # Phone numbers: catch common formats including international
        text = re.sub(r'\+?\d{1,3}[-\s]?\(?\d{3}\)?[-\s]?\d{3}[-\s]?\d{4}', lambda m: "***-***-" + re.sub(r'\D', '', m.group(0))[-4:], text)
        text = re.sub(r'\b[6-9]\d{9}\b', lambda m: "***-***-" + m.group(0)[-4:], text)
        text = re.sub(r'\+91\d{10}\b', lambda m: "+91-***-***-" + m.group(0)[-4:], text)

        # Redact OTPs (look for OTP/code/token and replace nearby digits)
        text = re.sub(r'(?i)(otp|code|token)(.*?)([0-9]{4,8})\b', r'\1\2[REDACTED]', text)

        # Redact passwords
        text = re.sub(r'(?i)(password|pwd|secret|key|token)\s*(=|:)\s*([^\s,\'\"]+)', r'\1\2[REDACTED]', text)

        return text

class PIIFilter(logging.Filter):
    """Filter for standard logging to redact PII in message and args."""
    def filter(self, record):
        if isinstance(record.msg, str):
            record.msg = PIIRedactor.redact_string(record.msg)

        if record.args:
            if isinstance(record.args, dict):
                new_args = {}
                for k, v in record.args.items():
                    if isinstance(v, str):
                        new_args[k] = PIIRedactor.redact_string(v)
                    else:
                        new_args[k] = v
                record.args = new_args
            elif isinstance(record.args, tuple) or isinstance(record.args, list):
                new_args = []
                for v in record.args:
                    if isinstance(v, str):
                        new_args.append(PIIRedactor.redact_string(v))
                    else:
                        new_args.append(v)
                record.args = tuple(new_args)

        return True

def redact_pii_structlog(logger, method_name, event_dict):
    """Structlog processor to redact PII from event data."""
    def _redact_dict(d):
        new_d = {}
        for k, v in d.items():
            if isinstance(v, str):
                new_d[k] = PIIRedactor.redact_string(v)
            elif isinstance(v, dict):
                new_d[k] = _redact_dict(v)
            elif isinstance(v, list) or isinstance(v, tuple):
                new_list = []
                for item in v:
                    if isinstance(item, str):
                        new_list.append(PIIRedactor.redact_string(item))
                    elif isinstance(item, dict):
                        new_list.append(_redact_dict(item))
                    else:
                        new_list.append(item)
                new_d[k] = type(v)(new_list)
            else:
                new_d[k] = v
        return new_d

    return _redact_dict(event_dict)

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

    # Apply standard library PII Filter to all handlers
    for handler in logging.root.handlers:
        handler.addFilter(PIIFilter())

    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        redact_pii_structlog,
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
