import logging
import sys

import structlog

import re

def mask_email(email):
    parts = email.split('@')
    if len(parts) == 2 and len(parts[0]) > 0:
        return f"{parts[0][0]}***@{parts[1]}"
    return "***REDACTED***"

def mask_phone(phone):
    digits = re.sub(r'\D', '', phone)
    if len(digits) >= 4:
        return f"***-***-{digits[-4:]}"
    return "***REDACTED***"

def redact_pii(logger, method_name, event_dict):
    sensitive_keys = ['password', 'secret', 'otp', 'email', 'phone', 'identifier']

    for key in list(event_dict.keys()):
        if not isinstance(key, str):
            continue
        lower_key = key.lower()
        if any(s in lower_key for s in sensitive_keys):
            val = str(event_dict[key])
            if 'email' in lower_key or '@' in val:
                event_dict[key] = mask_email(val)
            elif 'phone' in lower_key:
                event_dict[key] = mask_phone(val)
            else:
                event_dict[key] = '***REDACTED***'

    if 'event' in event_dict and isinstance(event_dict['event'], str):
        event_str = event_dict['event']

        def email_repl(match):
            return mask_email(match.group(0))
        event_str = re.sub(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', email_repl, event_str)

        event_str = re.sub(r'(?i)(otp(?:.*?))(\b\d{4,6}\b)', r'\g<1>***REDACTED***', event_str)

        event_str = re.sub(r'(?i)(phone(?:_number)?[\s=:]+)(\+?\d{10,15})', lambda m: m.group(1) + mask_phone(m.group(2)), event_str)

        def id_repl(match):
            val = match.group(2)
            if '@' in val:
                return match.group(1) + mask_email(val)
            elif re.match(r'^\+?\d+$', val):
                return match.group(1) + mask_phone(val)
            return match.group(0)

        event_str = re.sub(r'(?i)(for |to |identifier=)([^\s:]+)', id_repl, event_str)

        event_dict['event'] = event_str

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
        redact_pii,
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
