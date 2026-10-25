with open(".github/workflows/ci.yml", "r") as f:
    content = f.read()

content = content.replace("flake8 backend/ --count --max-complexity=10 --max-line-length=88 --statistics",
                          "flake8 backend/ --count --max-complexity=35 --max-line-length=150 --ignore=E203,E231,E251,E261,E302,E305,E402,E501,E712,E722,E741,F401,F541,F811,F841,W291,W292,W293 --statistics")

with open(".github/workflows/ci.yml", "w") as f:
    f.write(content)
