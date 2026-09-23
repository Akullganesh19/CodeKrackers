import logging
import re
import sys

import structlog

email_regex = re.compile(r"([a-zA-Z0-9_.+-]+)@([a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)")
phone_regex = re.compile(r"(\B\+[1-9]\d{6,14}\b)")
otp_regex = re.compile(r"(?i)(OTP.*?[\s:>-]+)(\d{6})\b")


def redact_str(text: str) -> str:
    text = email_regex.sub(r"***@\2", text)
    text = phone_regex.sub(r"[REDACTED_PHONE]", text)
    text = otp_regex.sub(r"\1[REDACTED_OTP]", text)
    return text


def redact_sensitive_data(logger, method_name, event_dict):
    def process_item(item):
        if isinstance(item, str):
            return redact_str(item)
        elif isinstance(item, dict):
            return {k: process_item(v) for k, v in item.items()}
        elif isinstance(item, (list, tuple)):
            return type(item)(process_item(i) for i in item)
        else:
            return item

    return {k: process_item(v) for k, v in event_dict.items()}


class RedactingFilter(logging.Filter):
    def filter(self, record):
        if isinstance(record.msg, str):
            record.msg = redact_str(record.msg)
        if record.args:
            if isinstance(record.args, dict):
                new_args = {}
                for k, v in record.args.items():
                    if isinstance(v, str):
                        new_args[k] = redact_str(v)
                    else:
                        new_args[k] = v
                record.args = new_args
            elif isinstance(record.args, tuple) or isinstance(record.args, list):
                new_args = []
                for arg in record.args:
                    if isinstance(arg, str):
                        arg = redact_str(arg)
                    new_args.append(arg)
                record.args = tuple(new_args)
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
        handler.addFilter(RedactingFilter())

    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        redact_sensitive_data,
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
