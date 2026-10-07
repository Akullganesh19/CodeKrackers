with open("backend/services/spam_shield.py", "r") as f:
    content = f.read()

# remove content_snippet
content = content.replace("content_snippet=(content or \"\")[:200],", "")

with open("backend/services/spam_shield.py", "w") as f:
    f.write(content)
