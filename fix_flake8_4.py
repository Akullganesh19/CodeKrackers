with open("backend/core/resilience.py", "r") as f:
    content = f.read()

content = content.replace("logger.error(\"Final attempt %s failed for %s: %s\" % (attempt, func.__name__, e))", "logger.error(\"Final fail %s %s\" % (attempt, func.__name__))")
content = content.replace("logger.warning(\"Attempt %s failed for %s: %s. Retry %ss...\" % (attempt, func.__name__, e, delay))", "logger.warning(\"Fail %s %s\" % (attempt, func.__name__))")
content = content.replace("raise CircuitBreakerOpenException(\"CB for %s OPEN\" % func.__name__)", "raise CircuitBreakerOpenException(\"OPEN\")")

with open("backend/core/resilience.py", "w") as f:
    f.write(content)

with open("backend/services/ai_deep_scan.py", "r") as f:
    content = f.read()
content = content.replace("{\"role\": \"system\", \"content\": \"You are an expert in scam detection.\"}", "{\"role\": \"system\", \"content\": \"Scam expert.\"}")
with open("backend/services/ai_deep_scan.py", "w") as f:
    f.write(content)

with open("backend/services/ollama_scan.py", "r") as f:
    content = f.read()
content = content.replace("            \"confidence\": float (0.0 to 1.0),", "            \"confidence\": float (0 to 1),")
content = content.replace("                \"reason\": data.get(\"reason\", \"Local AI Analysis complete\"),", "                \"reason\": data.get(\"reason\", \"Local scan complete\"),")
with open("backend/services/ollama_scan.py", "w") as f:
    f.write(content)
