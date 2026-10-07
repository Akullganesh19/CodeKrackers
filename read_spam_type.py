with open("backend/models/orm.py", "r") as f:
    content = f.read()
idx = content.find("class SpamType")
if idx != -1:
    print(content[idx:idx + 150])
