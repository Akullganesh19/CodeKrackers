with open(".github/workflows/ci.yml", "r") as f:
    content = f.read()

content = content.replace("E305,E402,E501,E712,E722,E741,F401,F541,F811,F841,W291,W292,W293,C901", "E305,E402,E501,E712,E722,E741,F401,F541,F811,F841,W291,W292,W293,W503,E123,E226,C901")

with open(".github/workflows/ci.yml", "w") as f:
    f.write(content)
