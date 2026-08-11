import logging
import sys
import re
import json

import structlog

EMAIL_REGEX = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
PHONE_REGEX = r'(?<!\d)(?:\+?[0-9]{1,3}[ -]?)?[0-9]{10}(?!\d)'

def mask_email(match):
    email = match.group(0)
    parts = email.split('@')
    if len(parts) != 2:
        return email
    user, domain = parts
    masked_user = user[0] + "***" + user[-1] if len(user) > 2 else user[0] + "***"
    return f"{masked_user}@{domain}"

def mask_phone(match):
    phone = match.group(0)
    digits = re.sub(r'\D', '', phone)
    if len(digits) >= 10:
        return f"***-***-{digits[-4:]}"
    return "***"

def redact_string(text):
    text = re.sub(EMAIL_REGEX, mask_email, text)
    text = re.sub(PHONE_REGEX, mask_phone, text)
    return text

class RedactingFormatter(logging.Formatter):
    def format(self, record):
        original = super().format(record)
        # Avoid corrupting JSON payloads
        try:
            json.loads(original)
            return original
        except ValueError:
            return redact_string(original)

def redact_processor(logger, log_method, event_dict):
    """
    A structlog processor that redacts emails and phone numbers recursively from the event dict.
    """
    def traverse_and_redact(d):
        for key, value in d.items():
            if isinstance(value, str):
                if value.startswith("{") and value.endswith("}"):
                    try:
                        import json
                        json.loads(value)
                        continue
                    except ValueError:
                        pass
                d[key] = redact_string(value)
            elif isinstance(value, dict):
                traverse_and_redact(value)
            elif isinstance(value, list):
                for i in range(len(value)):
                    if isinstance(value[i], str):
                        if value[i].startswith("{") and value[i].endswith("}"):
                            try:
                                import json
                                json.loads(value[i])
                                continue
                            except ValueError:
                                pass
                        value[i] = redact_string(value[i])
                    elif isinstance(value[i], dict):
                        traverse_and_redact(value[i])
        return d

    return traverse_and_redact(event_dict)

def setup_logging(json_logs: bool = True, log_level: int = logging.INFO):
    """
    Configure standard logging and structlog.
    """
    formatter = RedactingFormatter("%(message)s")
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    # Configure standard logging to use RedactingFormatter but route to stdout directly if bypassing structlog for standard logs
    # Alternatively, just basic config to stdout
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )
    # Re-apply the redacting formatter to the root logger's handler (basicConfig adds one)
    root_logger = logging.getLogger()
    if root_logger.handlers:
        root_logger.handlers[0].setFormatter(formatter)

    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        redact_processor,
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
