with open(".github/workflows/ci.yml", "r") as f:
    content = f.read()

content = content.replace("pip install black flake8 pytest pytest-asyncio isort mypy", "pip install black flake8 pytest pytest-asyncio isort mypy email-validator redis sendgrid twilio pyjwt slowapi")

with open(".github/workflows/ci.yml", "w") as f:
    f.write(content)
