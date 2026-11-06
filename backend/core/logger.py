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

    def redact_sensitive_data(logger, method_name, event_dict):
        SENSITIVE_KEYS = {"email", "phone", "password", "secret", "otp", "token", "access_token", "ssn"}

        for key, value in list(event_dict.items()):
            if isinstance(key, str):
                key_lower = key.lower()
                if any(sensitive in key_lower for sensitive in SENSITIVE_KEYS):
                    if isinstance(value, str):
                        if any(k in key_lower for k in ["password", "secret", "otp", "token", "ssn"]):
                            event_dict[key] = "[REDACTED]"
                        elif "@" in value:
                            parts = value.split("@")
                            if len(parts) == 2 and len(parts[0]) > 0:
                                event_dict[key] = f"{parts[0][0]}***@{parts[1]}"
                            else:
                                event_dict[key] = "[REDACTED]"
                        elif "phone" in key_lower:
                            digits = re.sub(r'\D', '', value)
                            if len(digits) >= 4:
                                event_dict[key] = f"***-{digits[-4:]}"
                            else:
                                event_dict[key] = "[REDACTED]"
                        else:
                            event_dict[key] = "[REDACTED]"
                    else:
                        event_dict[key] = "[REDACTED]"

        event = event_dict.get("event")
        if isinstance(event, str):
            def mask_email(match):
                local, domain = match.group(1), match.group(2)
                if len(local) > 0:
                    return f"{local[0]}***@{domain}"
                return f"***@{domain}"

            event = re.sub(r"([a-zA-Z0-9_.+-]+)@([a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)", mask_email, event)

            def mask_phone(match):
                prefix = match.group(1)
                phone = match.group(2)
                digits = re.sub(r'\D', '', phone)
                if len(digits) >= 4:
                    return f"{prefix}***-{digits[-4:]}"
                return f"{prefix}[REDACTED]"

            event = re.sub(r"(?i)(phone=)([^\s,]+)", mask_phone, event)
            event_dict["event"] = event

        return event_dict

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
