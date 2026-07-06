import re

files = {
    "backend/api/auth.py": [(r'logger\.error\(f"EMAIL_GATEWAY_ERROR: Failed to send OTP to \{otp_in\.identifier\}: \{e\}"\)', r'logger.error(\n                f"EMAIL_GATEWAY_ERROR: Failed to send OTP "\n                f"to {otp_in.identifier}: {e}"\n            )')],
    "backend/core/resilience.py": [
        (r'logger\.error\(\n                                f"Function \{func\.__name__\} failed "\n                                f"after \{max_attempts\} attempts\. Last error: \{e\}"\n                            \)', r'logger.error(\n                                f"Function {func.__name__} "\n                                f"failed after {max_attempts} attempts. "\n                                f"Last error: {e}"\n                            )'),
        (r'logger\.warning\(\n                                f"Function \{func\.__name__\} failed attempt "\n                                f"\{attempt\}/\{max_attempts\}: \{e\}\. "\n                                f"Retrying in \{delay\}s\.\.\."\n                            \)', r'logger.warning(\n                                f"Function {func.__name__} "\n                                f"failed attempt {attempt}/{max_attempts}: "\n                                f"{e}. Retrying in {delay}s..."\n                            )'),
        (r'logger\.info\(f"CircuitBreaker for \{func_name\} entering HALF_OPEN state"\)', r'logger.info(\n                    f"CircuitBreaker for {func_name} entering HALF_OPEN state"\n                )')
    ],
    "backend/services/ai_deep_scan.py": [
        (r'\{"role": "system", "content": "You are a cybersecurity expert specializing "\\n             "in Vishing and Smishing detection\."\}', r'{"role": "system", "content": "You are a cybersecurity "\n             "expert specializing in Vishing and Smishing detection."}'),
        (r'Content: "\{content\}"\s+', r'Content: "{content}"\n')
    ],
    "backend/services/notifier.py": [
        (r'logger\.warning\("Twilio credentials missing\. Notification skipped\."\)', r'logger.warning(\n            "Twilio credentials missing. Notification skipped."\n        )')
    ]
}

for filepath, replacements in files.items():
    with open(filepath, "r") as f:
        content = f.read()

    for search, replace in replacements:
        content = re.sub(search, replace, content)

    with open(filepath, "w") as f:
        f.write(content)
