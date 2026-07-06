import logging
import sys
import re

import structlog

SENSITIVE_KEYS = {"email", "phone", "identifier", "password", "otp", "token"}
EMAIL_REGEX = re.compile(r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)")
PHONE_REGEX = re.compile(r"(\+?\d{1,3}[\s-]?)?\(?\d{3}\)?[\s-]?\d{3}[\s-]?\d{4}")


def redact_string(s: str) -> str:
    s = EMAIL_REGEX.sub(
        lambda m: (
            m.group(1)[0] + "***@" + m.group(1).split("@")[1]
            if "@" in m.group(1)
            else "[REDACTED EMAIL]"
        ),
        s,
    )
    # Be careful not to overly redact numbers, simple phone regex
    s = PHONE_REGEX.sub("[REDACTED PHONE]", s)
    return s


def redact_dict(d: dict) -> dict:
    for k, v in d.items():
        if isinstance(k, str):
            kl = k.lower()
            if kl in SENSITIVE_KEYS or any(
                sk in kl and (kl.startswith(sk + "_") or kl.endswith("_" + sk))
                for sk in SENSITIVE_KEYS
            ):
                d[k] = "[REDACTED]"
                continue

        if isinstance(v, dict):
            redact_dict(v)
        elif isinstance(v, list):
            d[k] = [
                (
                    redact_dict(i)
                    if isinstance(i, dict)
                    else (redact_string(str(i)) if isinstance(i, str) else i)
                )
                for i in v
            ]
        elif isinstance(v, str):
            d[k] = redact_string(v)
    return d


def redact_pii(logger, log_method, event_dict):
    """
    Structlog processor to redact PII from logs.
    """
    return redact_dict(event_dict)


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
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        redact_pii,
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
