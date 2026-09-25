with open(".github/workflows/ci.yml", "r") as f:
    content = f.read()

content = content.replace("uses: actions/checkout@v3", "uses: actions/checkout@v4")
content = content.replace("uses: actions/setup-python@v4", "uses: actions/setup-python@v5")

with open(".github/workflows/ci.yml", "w") as f:
    f.write(content)
