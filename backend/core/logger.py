import logging
import sys
import re

import structlog

SENSITIVE_KEYS = {"phone", "phone_number", "otp", "ssn", "password", "card_number"}

# Masking functions
def mask_email(email: str) -> str:
    parts = email.split('@')
    if len(parts) != 2:
        return "[REDACTED]"
    user, domain = parts
    if len(user) > 1:
        masked_user = user[0] + "***"
    else:
        masked_user = "***"
    return f"{masked_user}@{domain}"

def mask_phone(phone: str) -> str:
    if len(phone) > 4:
        return "*" * (len(phone) - 4) + phone[-4:]
    return "[REDACTED]"

PHONE_REGEX = re.compile(r"(phone=|to\s+|for\s+)(\+?\d{7,15})", re.IGNORECASE)
OTP_REGEX = re.compile(r"(OTP.*?->\s*|code\s*:\s*|->\s*)(\d{4,6})", re.IGNORECASE)
EMAIL_CTX = re.compile(r"(email=|for\s+|to\s+)([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)", re.IGNORECASE)
SSN_REGEX = re.compile(r"(ssn=|ssn\s+)(\d{3}-\d{2}-\d{4}|\d{9})", re.IGNORECASE)

def redact_string(text: str) -> str:
    if not isinstance(text, str):
        return text

    def repl_phone(m):
        return m.group(1) + mask_phone(m.group(2))

    def repl_otp(m):
        return m.group(1) + "[REDACTED]"

    def repl_email(m):
        return m.group(1) + mask_email(m.group(2))

    def repl_ssn(m):
        return m.group(1) + "[REDACTED]"

    text = PHONE_REGEX.sub(repl_phone, text)
    text = OTP_REGEX.sub(repl_otp, text)
    text = EMAIL_CTX.sub(repl_email, text)
    text = SSN_REGEX.sub(repl_ssn, text)

    return text

def redact_pii(logger, log_method, event_dict):
    """
    structlog processor that recursively traverses log events to mask sensitive data
    (emails, phone numbers, OTPs) and fully redacts structured kwargs matching sensitive fields.
    """
    def _traverse_and_redact(obj):
        if isinstance(obj, dict):
            new_obj = {}
            for k, v in obj.items():
                is_sensitive = False
                if isinstance(k, str):
                    kl = k.lower()
                    if kl in SENSITIVE_KEYS or kl == "email":
                        is_sensitive = True

                if is_sensitive:
                    if isinstance(k, str) and k.lower() == "email" and isinstance(v, str):
                        new_obj[k] = mask_email(v)
                    elif isinstance(k, str) and ("phone" in k.lower()) and isinstance(v, str):
                        new_obj[k] = mask_phone(v)
                    else:
                        new_obj[k] = "[REDACTED]"
                else:
                    new_obj[k] = _traverse_and_redact(v)
            return new_obj
        elif isinstance(obj, list):
            return [_traverse_and_redact(item) for item in obj]
        elif isinstance(obj, str):
            return redact_string(obj)
        else:
            return obj

    return _traverse_and_redact(event_dict)

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
