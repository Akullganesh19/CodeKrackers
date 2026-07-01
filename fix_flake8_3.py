with open("backend/core/resilience.py", "r") as f:
    content = f.read()

content = content.replace("logger.error(\n                                f\"Final attempt {attempt} failed for {func.__name__}: {e}\"\n                            )", "logger.error(\"Final attempt %s failed for %s: %s\" % (attempt, func.__name__, e))")
content = content.replace("logger.warning(\n                            f\"Attempt {attempt} failed for {func.__name__}: {e}. Retrying in {delay}s...\"\n                        )", "logger.warning(\"Attempt %s failed for %s: %s. Retry %ss...\" % (attempt, func.__name__, e, delay))")
content = content.replace("logger.info(\n                            f\"Circuit Breaker for {func.__name__} entering HALF_OPEN state.\"\n                        )", "logger.info(\"CB for %s HALF_OPEN\" % func.__name__)")
content = content.replace("raise CircuitBreakerOpenException(\n                            f\"Circuit breaker for {func.__name__} is OPEN.\"\n                        )", "raise CircuitBreakerOpenException(\"CB for %s OPEN\" % func.__name__)")
content = content.replace("logger.info(\n                            f\"Circuit Breaker for {func.__name__} CLOSED. Service recovered.\"\n                        )", "logger.info(\"CB for %s CLOSED\" % func.__name__)")
content = content.replace("logger.error(\n                            f\"Circuit Breaker for {func.__name__} TRIPPED OPEN after {failures} failures.\"\n                        )", "logger.error(\"CB for %s TRIPPED OPEN\" % func.__name__)")

with open("backend/core/resilience.py", "w") as f:
    f.write(content)
