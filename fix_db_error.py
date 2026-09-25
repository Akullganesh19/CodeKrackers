with open(".github/workflows/ci.yml", "r") as f:
    content = f.read()

# Make sure we give permissions or ignore db initialization
content = content.replace("POSTGRES_USER: postgres", "POSTGRES_USER: root\n          POSTGRES_HOST_AUTH_METHOD: trust")
content = content.replace("DATABASE_URL: postgresql://postgres:testpassword@localhost:5432/vas_test_db", "DATABASE_URL: postgresql://root:testpassword@localhost:5432/vas_test_db")

with open(".github/workflows/ci.yml", "w") as f:
    f.write(content)
