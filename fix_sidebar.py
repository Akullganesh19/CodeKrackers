with open("app/components/Sidebar.tsx", "r") as f:
    content = f.read()

content = content.replace("} Activity, from 'lucide-react'", "  Activity,\n} from 'lucide-react'")

with open("app/components/Sidebar.tsx", "w") as f:
    f.write(content)
