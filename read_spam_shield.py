with open("backend/services/spam_shield.py", "r") as f:
    content = f.read()

decision_idx = content.find("# ── Decision ──")
if decision_idx != -1:
    print(content[decision_idx:decision_idx + 300])
else:
    print("Not found")
