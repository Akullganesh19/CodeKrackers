with open("backend/services/ai_deep_scan.py", "r") as f:
    content = f.read()

content = content.replace("{\"role\": \"system\", \"content\": \"Scam expert.\"}", "{\"role\": \"system\",\n             \"content\": \"Scam expert.\"}")
content = content.replace("model=getattr(settings, 'GROQ_MODEL', 'llama3-8b-8192'),", "model=getattr(\n            settings, 'GROQ_MODEL', 'llama3-8b-8192'\n        ),")

with open("backend/services/ai_deep_scan.py", "w") as f:
    f.write(content)

with open("backend/services/ollama_scan.py", "r") as f:
    content = f.read()
content = content.replace("            \"confidence\": float (0 to 1),", "            \"confidence\": float,")
content = content.replace("                \"score_increase\": round(data.get(\"confidence\", 0.0), 2) if data.get(\"is_scam\") else 0.0,", "                \"score_increase\": round(data.get(\"confidence\", 0.0), 2)\n                if data.get(\"is_scam\")\n                else 0.0,")
with open("backend/services/ollama_scan.py", "w") as f:
    f.write(content)
