import os
import re

files_to_fix = [
    "app/safety-score/page.tsx",
    "app/components/RobotBackground.tsx",
    "app/components/RobotLandingPage.tsx"
]

def fix_setmounted(filepath):
    if not os.path.exists(filepath):
        return
    with open(filepath, "r") as f:
        content = f.read()
    content = content.replace("setMounted(true)", "setTimeout(() => setMounted(true), 0)")
    with open(filepath, "w") as f:
        f.write(content)

for f in files_to_fix:
    fix_setmounted(f)

print("Fixed setMounted issues")
