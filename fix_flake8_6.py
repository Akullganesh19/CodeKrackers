with open("backend/services/ollama_scan.py", "r") as f:
    content = f.read()

content = content.replace("    response.raise_for_status()  # Raise error for bad status codes so retries can catch it", "    response.raise_for_status()  # Raise error for retries")
content = content.replace("            raise e  # re-raise to be caught by outer try-except and return default fallback", "            raise e  # re-raise to be caught by outer try")
with open("backend/services/ollama_scan.py", "w") as f:
    f.write(content)

with open("backend/services/ai_deep_scan.py", "r") as f:
    content = f.read()
content = content.replace("            {\"role\": \"system\",", "            {")
content = content.replace("             \"content\": \"Scam expert.\"}", "                \"role\": \"system\",\n                \"content\": \"Scam expert.\",\n            }")

with open("backend/services/ai_deep_scan.py", "w") as f:
    f.write(content)
