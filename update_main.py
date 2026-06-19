import re

main_file = "backend/main.py"
with open(main_file, "r") as f:
    content = f.read()

import_statement = "from .core.events.listeners import setup_listeners\n"
if "from .core.events.listeners import setup_listeners" not in content:
    content = content.replace("from .scheduler import setup_scheduler", "from .scheduler import setup_scheduler\n" + import_statement)

init_target = """
    # setup_scheduler()

    # Initialize Event Bus listeners for Cross-System Intelligence
    setup_listeners()
"""
if "setup_listeners()" not in content:
    content = content.replace("    # setup_scheduler()", init_target)

with open(main_file, "w") as f:
    f.write(content)
