import logging
import sys

import structlog

import re

def redact_sensitive_data(logger, method_name, event_dict):
    SENSITIVE_KEYS = {"password", "secret", "otp", "ssn"}
    PARTIAL_KEYS = {"email", "phone", "phone_number"}

    for key in list(event_dict.keys()):
        if isinstance(key, str):
            k = key.lower()
            if k in SENSITIVE_KEYS:
                event_dict[key] = "***REDACTED***"
            elif k in PARTIAL_KEYS:
                val = str(event_dict[key])
                if k == "email" and "@" in val:
                    parts = val.split("@")
                    if len(parts[0]) > 0:
                        event_dict[key] = f"{parts[0][0]}***@{parts[1]}"
                    else:
                        event_dict[key] = f"***@{parts[1]}"
                elif k in ["phone", "phone_number"]:
                    if len(val) > 4:
                        event_dict[key] = val[:3] + "***" + val[-2:]
                    else:
                        event_dict[key] = "***REDACTED***"

    # Mask event string
    event_str = event_dict.get("event")
    if isinstance(event_str, str):
        # Email
        event_str = re.sub(
            r'([a-zA-Z0-9])([a-zA-Z0-9_.+-]*)(@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)',
            lambda m: f"{m.group(1)}***{m.group(3)}",
            event_str
        )
        # Phone
        event_str = re.sub(
            r'\+?\d{10,15}',
            lambda m: m.group(0)[:3] + "***" + m.group(0)[-2:] if len(m.group(0)) > 4 else "***REDACTED***",
            event_str
        )

        # Specific OTP message format: "SIMULATED OTP SENT TO +12345678901: 123456"
        event_str = re.sub(
            r'(?i)(OTP\s+(?:SENT TO|sent to)\s+\S+:\s*)(\d+)',
            r'\1***REDACTED***',
            event_str
        )

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
