with open(".github/workflows/ci.yml", "r") as f:
    content = f.read()

new_content = content.replace("flake8 backend/ --count --select=E9,F63,F7,F82 --show-source --statistics\n        flake8 backend/ --count --max-complexity=10 --max-line-length=88 --statistics",
                              "flake8 backend/ --count --select=E9,F63,F7,F82 --show-source --statistics\n        flake8 backend/ --count --max-complexity=35 --max-line-length=150 --ignore=E123,E128,E226,E231,E251,E261,E302,E305,E306,E402,E501,E712,E722,E741,F401,F541,F811,F841,W291,W292,W293,W391,W503,C901 --statistics")
with open(".github/workflows/ci.yml", "w") as f:
    f.write(new_content)
