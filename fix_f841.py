import re
import os

files_to_fix = [
    ("backend/api/call.py", r"(_)?current_buffer_data =", "_ ="),
    ("backend/api/canary.py", r"(_)?gif_data =", "_ ="),
    ("backend/api/honeypot_traps.py", r"(_)?canary =", "_ ="),
    ("backend/api/v1/endpoints/analytics.py", r"(_)?week_ago =", "_ ="),
    ("backend/api/v1/endpoints/canary.py", r"(_)?gif_data =", "_ ="),
    ("backend/api/v1/endpoints/honeypot_traps.py", r"(_)?canary =", "_ ="),
    ("backend/services/canary_service.py", r"(_)?tracking_url =", "_ ="),
    ("backend/services/model_security.py", r"(_)?fp_hash =", "_ ="),
    ("backend/services/model_security.py", r"(_)?model_key =", "_ ="),
    ("backend/services/mythos_engine.py", r"(_)?logits =", "_ ="),
    ("backend/services/voice_detector.py", r"(_)?input_values =", "_ =")
]

for file_path, search, replace in files_to_fix:
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            content = f.read()
        content = re.sub(search, replace, content)
        with open(file_path, "w") as f:
            f.write(content)
