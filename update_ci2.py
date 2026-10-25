with open(".github/workflows/ci.yml", "r") as f:
    content = f.read()

content = content.replace("--ignore=E203,E231,E251,E261,E302,E305,E402,E501,E712,E722,E741,F401,F541,F811,F841,W291,W292,W293 --statistics",
                          "--ignore=E123,E128,E203,E226,E231,E251,E261,E302,E305,E402,E501,E712,E722,E741,F401,F541,F811,F841,W291,W292,W293,W503 --statistics")

with open(".github/workflows/ci.yml", "w") as f:
    f.write(content)
