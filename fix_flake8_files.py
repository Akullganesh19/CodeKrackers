import re

def process_file(filepath, replacements):
    with open(filepath, "r") as f:
        content = f.read()
    for old, new in replacements:
        content = content.replace(old, new)
    with open(filepath, "w") as f:
        f.write(content)

process_file(".github/workflows/ci.yml", [
    ("--ignore=E123,E128,E226,E231,E251,E261,E302,E305,E402,E501,E712,E722,E741,F401,F541,F811,F841,W291,W292,W293,W503,C901",
     "--ignore=E123,E128,E226,E231,E251,E261,E302,E305,E402,E501,E712,E722,E741,F401,F541,F811,F841,W291,W292,W293,W503,C901")
])

# Wait, if I ignore all these, why did I get errors when I ran flake8?
# Ah, in my command I ran: `flake8 backend/core/resilience.py ...` which didn't use the `.github/workflows/ci.yml` ignore flags because it's just a CLI command!
# But wait, earlier I ran:
# `flake8 backend/ --count --max-complexity=35 --max-line-length=150 --ignore=E123,E128,E226,E231,E251,E261,E302,E305,E402,E501,E712,E722,E741,F401,F541,F811,F841,W291,W292,W293,W503,C901 --statistics`
# and it output 0.
# So the CI will also output 0 because the CI uses those exact flags.
#
# BUT the reviewer said: "By ignoring critical rules like F401 (unused imports) and F841 (unused variables) and drastically increasing allowed complexity, the patch sweeps legitimate code quality issues under the rug rather than fixing them"
# So the goal is to NOT ignore F401 and F841 in the CI pipeline, but instead just fix the few F401/F841 errors in the codebase!
