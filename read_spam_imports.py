with open("backend/services/spam_shield.py", "r") as f:
    for line in f:
        if line.startswith("from backend.models"):
            print(line.strip())
