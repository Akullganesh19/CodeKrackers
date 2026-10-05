with open("backend/api/detection.py", "r") as f:
    content = f.read()

content = content.replace("messages=[", "messages = [")

with open("backend/api/detection.py", "w") as f:
    f.write(content)
