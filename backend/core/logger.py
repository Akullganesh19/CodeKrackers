import logging
import sys

import structlog

import re
import copy

def redact_pii(logger, method_name, event_dict):
    event_dict = copy.deepcopy(event_dict)

    # regexes with context boundaries or explicit patterns
    email_regex = re.compile(r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)")
    phone_context_regex = re.compile(r"(phone=|to |TO )(\+?[0-9]{7,15})")
    otp_regex = re.compile(r"(OTP.*? )(\+?[0-9]{7,15}: )?([a-zA-Z0-9]{6})\b")

    def _mask_email(match):
        email = match.group(1)
        if "@" in email:
            local, domain = email.split("@", 1)
            masked_local = local[0] + "***" if len(local) > 1 else "***"
            return f"{masked_local}@{domain}"
        return "***"

    def _mask_phone(match):
        prefix = match.group(1)
        phone = match.group(2)
        masked_phone = phone[:3] + "***" + phone[-2:] if len(phone) > 5 else "***"
        return f"{prefix}{masked_phone}"

    def _mask_otp(match):
        prefix = match.group(1)
        phone_part = match.group(2) or ""
        otp = match.group(3)
        return f"{prefix}{phone_part}***"

    def redact_string(text: str) -> str:
        text = email_regex.sub(_mask_email, text)
        text = phone_context_regex.sub(_mask_phone, text)
        text = otp_regex.sub(_mask_otp, text)
        return text

    def traverse_and_redact(data):
        if isinstance(data, str):
            return redact_string(data)
        elif isinstance(data, dict):
            return {k: traverse_and_redact(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [traverse_and_redact(item) for item in data]
        return data

    for k, v in event_dict.items():
        if k in ["phone", "phone_number"] and isinstance(v, str):
            masked_phone = v[:3] + "***" + v[-2:] if len(v) > 5 else "***"
            event_dict[k] = masked_phone
        elif k in ["email", "identifier"] and isinstance(v, str) and "@" in v:
            local, domain = v.split("@", 1)
            masked_local = local[0] + "***" if len(local) > 1 else "***"
            event_dict[k] = f"{masked_local}@{domain}"
        else:
            event_dict[k] = traverse_and_redact(v)

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
