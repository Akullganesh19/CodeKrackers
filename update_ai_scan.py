import re

with open("backend/services/ai_deep_scan.py", "r") as f:
    content = f.read()

import_stmt = "from backend.core.resilience import with_retries, circuit_breaker\n"
if "from backend.core.resilience" not in content:
    content = content.replace("from backend.core.config import settings", "from backend.core.config import settings\n" + import_stmt)

helpers = """
@with_retries(max_attempts=3, base_delay=0.5)
@circuit_breaker(failure_threshold=5, recovery_timeout=120.0)
def _call_groq_api(prompt: str) -> dict:
    client = Groq(api_key=settings.GROQ_API_KEY)
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a cybersecurity expert specializing in Vishing and Smishing detection."},
            {"role": "user", "content": prompt}
        ],
        model=settings.GROQ_MODEL if hasattr(settings, 'GROQ_MODEL') else 'llama3-8b-8192',
        response_format={"type": "json_object"}
    )
    import json
    return json.loads(chat_completion.choices[0].message.content)

"""
if "_call_groq_api" not in content:
    content = content.replace("def ai_deep_scan(content: str, source_type: str = \"sms\") -> Dict[str, Any]:", helpers + "\ndef ai_deep_scan(content: str, source_type: str = \"sms\") -> Dict[str, Any]:")


search_str = """        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a cybersecurity expert specializing in Vishing and Smishing detection."},
                {"role": "user", "content": prompt}
            ],
            model=settings.GROQ_MODEL,
            response_format={"type": "json_object"}
        )

        import json
        result = json.loads(chat_completion.choices[0].message.content)"""

replace_str = "        result = _call_groq_api(prompt)"

content = content.replace(search_str, replace_str)

search_str2 = """        client = Groq(api_key=settings.GROQ_API_KEY)

        prompt = f\"\"\"
        Analyze this {source_type} for potential scam/phishing intent.
        Content: "{content}"

        Provide a JSON response with:
        1. "is_scam": boolean
        2. "confidence": float (0-1)
        3. "reason": string summary
        4. "risk_factors": list of strings
        \"\"\""""

replace_str2 = """        prompt = f\"\"\"
        Analyze this {source_type} for potential scam/phishing intent.
        Content: "{content}"

        Provide a JSON response with:
        1. "is_scam": boolean
        2. "confidence": float (0-1)
        3. "reason": string summary
        4. "risk_factors": list of strings
        \"\"\""""
content = content.replace(search_str2, replace_str2)

with open("backend/services/ai_deep_scan.py", "w") as f:
    f.write(content)
