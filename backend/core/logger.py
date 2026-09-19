import logging
import re
import sys

import structlog

EMAIL_RE = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
PHONE_RE = re.compile(r"\B\+[1-9]\d{6,14}\b")
# Ensure we don't redact just any random string. Code/OTP might look like numbers.
OTP_RE = re.compile(r"(?i)(otp|password|code|token)(.*?:\s*|.*?->\s*)([a-zA-Z0-9_.-]+)")
# Key pattern for dictionary kwargs redaction
SENSITIVE_KEY_RE = re.compile(r"(?i)(otp|password|code|token)")


def redact_email(match):
    email = match.group(0)
    if "@" in email:
        local, domain = email.split("@", 1)
        if len(local) > 1:
            local = local[0] + "***"
        else:
            local = "***"
        return f"{local}@{domain}"
    return "***"


def redact_phone(match):
    phone = match.group(0)
    if len(phone) > 5:
        return phone[:3] + "***" + phone[-2:]
    return "***"


def redact_string(text):
    if not isinstance(text, str):
        text = str(text)

    text = EMAIL_RE.sub(redact_email, text)
    text = PHONE_RE.sub(redact_phone, text)
    text = OTP_RE.sub(r"\1\2***", text)
    return text


class RedactingFilter(logging.Filter):
    def filter(self, record):
        if record.msg is not None:
            redacted_msg = redact_string(record.msg)
            if redacted_msg != str(record.msg):
                record.msg = redacted_msg

        if isinstance(record.args, tuple):
            new_args = []
            for arg in record.args:
                redacted_arg = redact_string(arg)
                if redacted_arg != str(arg):
                    new_args.append(redacted_arg)
                else:
                    new_args.append(arg)
            record.args = tuple(new_args)
        elif isinstance(record.args, dict):
            new_args = {}
            for k, v in record.args.items():
                if SENSITIVE_KEY_RE.search(k):
                    new_args[k] = "***"
                else:
                    redacted_v = redact_string(v)
                    if redacted_v != str(v):
                        new_args[k] = redacted_v
                    else:
                        new_args[k] = v
            record.args = new_args

        return True


def redact_sensitive_data(logger, log_method, event_dict):
    if "event" in event_dict:
        event_dict["event"] = redact_string(str(event_dict["event"]))

    if "positional_args" in event_dict:
        args = []
        for arg in event_dict["positional_args"]:
            args.append(redact_string(arg))
        event_dict["positional_args"] = tuple(args)

    for key, value in list(event_dict.items()):
        if key not in (
            "event",
            "positional_args",
            "timestamp",
            "level",
            "logger",
            "exc_info",
        ):
            if SENSITIVE_KEY_RE.search(key):
                event_dict[key] = "***"
            else:
                redacted_val = redact_string(value)
                if redacted_val != str(value):
                    event_dict[key] = redacted_val

    return event_dict


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

    # Add redacting filter to all standard library log handlers
    redacting_filter = RedactingFilter()
    for handler in logging.root.handlers:
        handler.addFilter(redacting_filter)

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
