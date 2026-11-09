import os
import re

for root, _, files in os.walk('app'):
    for file in files:
        if file.endswith('.tsx') or file.endswith('.ts'):
            path = os.path.join(root, file)
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
                matches = re.findall(r"fetch\(['\"]([^'\"]+)['\"]", content)
                for match in matches:
                    print(f"{path}: {match}")
