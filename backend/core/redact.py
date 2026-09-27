import logging
import re

# Redaction regexes
EMAIL_REGEX = re.compile(r"\b([a-zA-Z0-9._%+-]{1,2})[^@]*(@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b")
# E.164 phone numbers with mandatory leading +
PHONE_REGEX = re.compile(r"\B\+[1-9]\d{6,14}\b")


def _redact_email(match):
    """Keep first 1-2 chars of username and full domain (e.g., us***@example.com)"""
    return match.group(1) + "***" + match.group(2)


def _redact_phone(match):
    """Keep country code + first digit and last 2 digits (e.g., +12***01)"""
    full_phone = match.group(0)
    return full_phone[:3] + "***" + full_phone[-2:]


def redact_string(text: str) -> str:
    """Redact sensitive PII in a string."""
    text = EMAIL_REGEX.sub(_redact_email, text)
    text = PHONE_REGEX.sub(_redact_phone, text)
    return text


def redact_data(data: any) -> any:
    """Recursively redact PII from structures like dict, list, tuple."""
    if isinstance(data, str):
        return redact_string(data)
    elif isinstance(data, dict):
        return {k: redact_data(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [redact_data(v) for v in data]
    elif isinstance(data, tuple):
        return tuple(redact_data(v) for v in data)
    return data


def structlog_redactor(logger, method_name, event_dict):
    """Structlog processor to redact sensitive data from logs."""
    redacted_event_dict = {}
    for key, value in event_dict.items():
        redacted_event_dict[key] = redact_data(value)
    return redacted_event_dict


class RedactingFilter(logging.Filter):
    """Python standard logging filter to redact sensitive data from args and msg."""

    def filter(self, record):
        if hasattr(record, "args") and record.args:
            if isinstance(record.args, dict):
                record.args = {k: redact_data(v) for k, v in record.args.items()}
            elif isinstance(record.args, tuple):
                record.args = tuple(redact_data(v) for v in record.args)
            elif isinstance(record.args, list):
                record.args = [redact_data(v) for v in record.args]

        if hasattr(record, "msg") and isinstance(record.msg, str):
            record.msg = redact_string(record.msg)

        return True
