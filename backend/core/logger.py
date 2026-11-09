import logging
import sys
import re

import structlog

def redact_sensitive_data(logger, method_name, event_dict):
    sensitive_keys = {"password", "secret", "token", "otp", "otp_code", "access_token"}

    def _redact_dict(d):
        for key in list(d.keys()):
            if isinstance(key, str) and key.lower() in sensitive_keys:
                d[key] = "***"
            elif isinstance(d[key], dict):
                _redact_dict(d[key])

    _redact_dict(event_dict)

    if "event" in event_dict and isinstance(event_dict["event"], str):
        event_str = event_dict["event"]

        event_str = re.sub(r'([a-zA-Z0-9])[a-zA-Z0-9_.+-]*(@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)', r'\1***\2', event_str)
        event_str = re.sub(r'(\+\d{1,3}\d{3})\d{2,}(\d{2})', r'\1***\2', event_str)

        event_str = re.sub(r'(?:Generated|SIMULATED|FALLBACK|SMS) (?:OTP|code).*?(?:->|:)\s*(\d+)', lambda m: m.group(0).replace(m.group(1), '***'), event_str)

        event_dict["event"] = event_str

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
