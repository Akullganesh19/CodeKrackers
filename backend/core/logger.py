import logging
import sys

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

    import re

    EMAIL_REGEX = re.compile(r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)")
    PHONE_REGEX = re.compile(r"(?<!\d)(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}(?!\d)")
    OTP_REGEX = re.compile(r"(?<!\d)\d{6}(?!\d)")

    def mask_email(match):
        email = match.group(0)
        parts = email.split('@')
        if len(parts) == 2:
            user, domain = parts
            masked_user = user[0] + "***" if len(user) > 0 else "***"
            return f"{masked_user}@{domain}"
        return "***"

    def mask_phone(match):
        phone = match.group(0)
        chars = list(phone)
        digit_indices = [i for i, c in enumerate(chars) if c.isdigit()]
        if len(digit_indices) > 4:
            for i in digit_indices[:-4]:
                chars[i] = '*'
        return "".join(chars)

    def redact_pii(logger, log_method, event_dict):
        def redact_string(s: str) -> str:
            s = EMAIL_REGEX.sub(mask_email, s)
            s = PHONE_REGEX.sub(mask_phone, s)
            s = OTP_REGEX.sub("******", s)
            return s

        def recursively_redact(obj):
            if isinstance(obj, str):
                return redact_string(obj)
            elif isinstance(obj, (int, float)):
                # Convert to string to check if it matches OTP or Phone, then back to original type if no change
                s_obj = str(obj)
                redacted_s = redact_string(s_obj)
                if redacted_s != s_obj:
                    return redacted_s
                return obj
            elif isinstance(obj, dict):
                return {k: recursively_redact(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [recursively_redact(v) for v in obj]
            elif isinstance(obj, tuple):
                return tuple(recursively_redact(v) for v in obj)
            return obj

        for key, value in event_dict.items():
            event_dict[key] = recursively_redact(value)

        return event_dict

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
