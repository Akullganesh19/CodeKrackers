import logging
import sys
import re

import structlog

def redact_email(match):
    email = match.group(0)
    parts = email.split('@')
    if len(parts) == 2:
        name, domain = parts
        if len(name) > 1:
            name = name[0] + "***"
        else:
            name = "***"
        return f"{name}@{domain}"
    return email

def redact_phone(match):
    phone = match.group(0)
    if len(phone) > 5:
        return "+" + "*" * (len(phone) - 5) + phone[-4:]
    return phone

class PIIRedactor:
    def __init__(self):
        self.patterns = [
            (re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'), redact_email),
            (re.compile(r'\B\+[1-9]\d{6,14}\b'), redact_phone),
            (re.compile(r'\b\d{6}\b'), '***OTP***'),
        ]

    def redact(self, text):
        if not isinstance(text, str):
            return text
        for pattern, repl in self.patterns:
            text = pattern.sub(repl, text)
        return text

    def __call__(self, logger, log_method, event_dict):
        # Redact main event message
        if "event" in event_dict:
            event_dict["event"] = self.redact(str(event_dict["event"]))

        # Redact position arguments
        if "positional_args" in event_dict:
            new_args = []
            for arg in event_dict["positional_args"]:
                if isinstance(arg, str):
                    new_args.append(self.redact(arg))
                else:
                    new_args.append(arg)
            event_dict["positional_args"] = tuple(new_args)

        # Redact other kwargs values that are strings
        for key, value in list(event_dict.items()):
            if key not in ("event", "positional_args") and isinstance(value, str):
                event_dict[key] = self.redact(value)

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

    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        PIIRedactor(),
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
