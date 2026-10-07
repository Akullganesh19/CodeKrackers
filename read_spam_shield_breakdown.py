with open("backend/services/spam_shield.py", "r") as f:
    content = f.read()
idx = content.find("breakdown.append")
if idx != -1:
    print(content[idx:idx + 500])
