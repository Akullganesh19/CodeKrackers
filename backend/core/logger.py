import logging
import re
import sys

import structlog

email_regex = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")

# Match explicit E.164 phone numbers (e.g. +14155552671) safely without matching raw IDs.
phone_regex_e164 = re.compile(r"\B\+[1-9]\d{6,14}\b")

# Also redact specific keys known to contain sensitive data in structured logs
sensitive_keys = {"phone", "phone_number", "email", "address", "ssn"}


def mask_email(match):
    email = match.group(0) if hasattr(match, "group") else str(match)
    parts = email.split("@")
    if len(parts) != 2:
        return email
    user, domain = parts
    return f"{user[0]}***@{domain}" if len(user) > 0 else f"***@{domain}"


def mask_phone(match_or_str):
    phone = (
        match_or_str.group(0) if hasattr(match_or_str, "group") else str(match_or_str)
    )
    if len(phone) > 4:
        return phone[:-4] + "****"
    return phone


def mask_ssn(val):
    if len(val) > 4:
        return "***-**-" + val[-4:]
    return val


class RedactingFilter(logging.Filter):
    """
    Standard library filter to redact from msg and args before formatting.
    This avoids corrupting JSON output later.
    """

    def filter(self, record):
        if isinstance(record.msg, str):
            record.msg = email_regex.sub(mask_email, record.msg)
            record.msg = phone_regex_e164.sub(mask_phone, record.msg)

        if isinstance(record.args, dict):
            new_args = {}
            for k, v in record.args.items():
                if isinstance(v, str):
                    v = email_regex.sub(mask_email, v)
                    v = phone_regex_e164.sub(mask_phone, v)
                new_args[k] = v
            record.args = new_args
        elif isinstance(record.args, (list, tuple)):
            new_args = []
            for arg in record.args:
                if isinstance(arg, str):
                    arg = email_regex.sub(mask_email, arg)
                    arg = phone_regex_e164.sub(mask_phone, arg)
                new_args.append(arg)
            record.args = tuple(new_args)

        return True


def redact_nested_dict(data, key=None):
    if isinstance(data, dict):
        return {k: redact_nested_dict(v, key=k) for k, v in data.items()}
    elif isinstance(data, list):
        return [redact_nested_dict(i, key=key) for i in data]
    elif isinstance(data, str):
        val = email_regex.sub(mask_email, data)
        val = phone_regex_e164.sub(mask_phone, val)
        if key and key.lower() in sensitive_keys:
            if key.lower() == "email":
                return mask_email(val)
            elif key.lower() == "ssn":
                return mask_ssn(val)
            return mask_phone(val)
        return val
    elif isinstance(data, (int, float)) and key and key.lower() in sensitive_keys:
        return mask_phone(str(data))
    return data


def redact_structlog_processor(logger, log_method, event_dict):
    """
    Structlog processor to redact PII (emails, phones) from structured logs.
    """
    for key, value in event_dict.items():
        event_dict[key] = redact_nested_dict(value, key=key)
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

    redacting_filter = RedactingFilter()
    root_logger = logging.getLogger()
    for handler in root_logger.handlers:
        handler.addFilter(redacting_filter)

    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        redact_structlog_processor,  # Add redaction processor for structlog
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
