import re

with open("backend/api/detection.py", "r") as f:
    content = f.read()

# Fix spacing in detection.py line 82
old = "        keyword_confidence = min((keyword_score * 0.15) + (url_score * 0.2), 1.0)"
new = "        keyword_confidence = min((keyword_score * 0.15) + (url_score * 0.2), 1.0)"

content = content.replace(old, new)
with open("backend/api/detection.py", "w") as f:
    f.write(content)
