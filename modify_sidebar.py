import re

with open("app/components/Sidebar.tsx", "r") as f:
    content = f.read()

# Make sure Activity is in lucide-react import
if "Activity," not in content and "Activity }" not in content and "lucide-react" in content:
    content = content.replace("from 'lucide-react'", "  Activity,\n} from 'lucide-react'")

with open("app/components/Sidebar.tsx", "w") as f:
    f.write(content)
print("Updated Sidebar Activity import")
