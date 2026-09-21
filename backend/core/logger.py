import logging
import sys

import structlog

from backend.core.pii_redactor import redact_string


class PiiRedactingFilter(logging.Filter):
    def filter(self, record):
        if hasattr(record, "msg") and isinstance(record.msg, str):
            record.msg = redact_string(record.msg)

        if hasattr(record, "args") and record.args:
            # We must handle formatting properly. We can deepcopy the args
            # to avoid modifying application state, and stringify them to redact.
            # But the simplest and safest way for standard library args
            # is to convert all args to strings and redact them, if they are meant for %s formatting.
            def _safely_redact_arg(arg):
                if isinstance(arg, str):
                    return redact_string(arg)
                elif isinstance(arg, (int, float, bool, type(None))):
                    return arg
                else:
                    # For complex objects, stringify and redact, so they don't leak when formatted
                    return redact_string(str(arg))

            if isinstance(record.args, tuple):
                record.args = tuple(_safely_redact_arg(arg) for arg in record.args)
            elif isinstance(record.args, dict):
                record.args = {k: _safely_redact_arg(v) for k, v in record.args.items()}
        return True


def pii_redacting_processor(logger, log_method, event_dict):
    def _redact_dict(d):
        # We must create a new dictionary to avoid in-place mutation of application state
        new_d = {}
        for k, v in d.items():
            if isinstance(v, str):
                new_d[k] = redact_string(v)
            elif isinstance(v, dict):
                new_d[k] = _redact_dict(v)
            elif isinstance(v, list):
                new_d[k] = [
                    (
                        _redact_dict(i)
                        if isinstance(i, dict)
                        else (
                            redact_string(str(i))
                            if not isinstance(i, (int, float, bool, type(None)))
                            else i
                        )
                    )
                    for i in v
                ]
            else:
                if isinstance(v, (int, float, bool, type(None))):
                    new_d[k] = v
                else:
                    # Stringify objects that might contain PII when they are logged
                    new_d[k] = redact_string(str(v))
        return new_d

    return _redact_dict(event_dict)


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

    # Attach filter to all root handlers to intercept standard logging
    for handler in logging.root.handlers:
        handler.addFilter(PiiRedactingFilter())

    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        pii_redacting_processor,
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
