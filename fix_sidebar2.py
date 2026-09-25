with open("app/components/Sidebar.tsx", "r") as f:
    content = f.read()

content = content.replace("  Bell\n  Activity,", "  Bell,\n  Activity,")

with open("app/components/Sidebar.tsx", "w") as f:
    f.write(content)
