import re

files = {
    "backend/api/auth.py": [(r'(redis_client\.setex\(redis_key, settings\.OTP_EXPIRE_SECONDS, otp_code\))', r'redis_client.setex(\n            redis_key, settings.OTP_EXPIRE_SECONDS, otp_code\n        )')],
    "backend/core/resilience.py": [
        (r'logger\.error\(f"Function \{func\.__name__\} failed after \{max_attempts\} attempts\. Last error: \{e\}"\)', r'logger.error(\n                                f"Function {func.__name__} failed "\n                                f"after {max_attempts} attempts. Last error: {e}"\n                            )'),
        (r'logger\.warning\(f"Function \{func\.__name__\} failed attempt \{attempt\}/\{max_attempts\}: \{e\}\. Retrying in \{delay\}s\.\.\."\)', r'logger.warning(\n                                f"Function {func.__name__} failed attempt "\n                                f"{attempt}/{max_attempts}: {e}. "\n                                f"Retrying in {delay}s..."\n                            )'),
        (r'logger\.warning\(f"CircuitBreaker for \{func_name\} entering OPEN state after \{self\.failure_count\} failures"\)', r'logger.warning(\n                f"CircuitBreaker for {func_name} entering OPEN state "\n                f"after {self.failure_count} failures"\n            )')
    ],
    "backend/services/ai_deep_scan.py": [
        (r'\{"role": "system", "content": "You are a cybersecurity expert specializing in Vishing and Smishing detection\."\}', r'{"role": "system", "content": "You are a cybersecurity expert specializing "\n             "in Vishing and Smishing detection."}'),
        (r'\n        \n', r'\n')
    ],
    "backend/services/notifier.py": [
        (r'f"VAS Command Center: Your verification code is \{otp_code\}\. " "Valid for 5 minutes\. DO NOT share this with anyone\."', r'f"VAS Command Center: Your verification code is {otp_code}. "\n            "Valid for 5 minutes. DO NOT share this with anyone."')
    ],
    "backend/services/ollama_scan.py": [
        (r'\n        \n', r'\n')
    ]
}

for filepath, replacements in files.items():
    with open(filepath, "r") as f:
        content = f.read()

    for search, replace in replacements:
        content = re.sub(search, replace, content)

    with open(filepath, "w") as f:
        f.write(content)
