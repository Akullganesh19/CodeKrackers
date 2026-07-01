with open("backend/api/auth.py", "r") as f:
    content = f.read()

content = content.replace("plain_text_content=f\"Your VSDP code is: {otp_code}. Valid 5 mins. Do not share.\",", "plain_text_content=f\"Code: {otp_code}. Valid 5 mins. Don't share.\",")
with open("backend/api/auth.py", "w") as f:
    f.write(content)

with open("backend/core/resilience.py", "r") as f:
    content = f.read()
content = content.replace("logger.error(\"Final attempt %s failed for %s\" % (attempt, func.__name__))", "logger.error(\"Failed: %s\" % func.__name__)")
content = content.replace("logger.warning(\"Attempt %s failed: %s. Retry %ss\" % (attempt, e, delay))", "logger.warning(\"Retry %s: %s\" % (attempt, delay))")
content = content.replace("logger.info(\"CB for %s HALF_OPEN\" % func.__name__)", "logger.info(\"HALF_OPEN %s\" % func.__name__)")
content = content.replace("logger.info(\"CB for %s CLOSED\" % func.__name__)", "logger.info(\"CLOSED %s\" % func.__name__)")
content = content.replace("logger.error(\"CB for %s OPEN after %s fails\" % (func.__name__, failures))", "logger.error(\"OPEN %s\" % func.__name__)")
with open("backend/core/resilience.py", "w") as f:
    f.write(content)

with open("backend/services/ai_deep_scan.py", "r") as f:
    content = f.read()
content = content.replace("{\"role\": \"system\", \"content\": \"You are an expert in scam detection.\"}", "{\"role\": \"system\", \"content\": \"Scam expert.\"}")
with open("backend/services/ai_deep_scan.py", "w") as f:
    f.write(content)

with open("backend/services/ollama_scan.py", "r") as f:
    content = f.read()
content = content.replace("@circuit_breaker(failure_threshold=5, recovery_timeout=60.0)", "@circuit_breaker(5, 60.0)")
content = content.replace("logger.warning(f\"Ollama returned status {response.status_code}\")", "logger.warning(f\"Ollama status {response.status_code}\")")
with open("backend/services/ollama_scan.py", "w") as f:
    f.write(content)
