import subprocess
import time
import os
import sys

def start_services():
    print("====================================================")
    print("VAS SENTINEL: AUTONOMOUS BACKGROUND DAEMON")
    print("====================================================")
    
    services = [
        {
            "name": "FastAPI Backend",
            "command": ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"],
            "cwd": os.path.dirname(os.path.abspath(__file__))
        },
        {
            "name": "OpenClaw Gateway",
            "command": ["openclaw", "gateway", "--force"],
            "cwd": os.path.dirname(os.path.abspath(__file__))
        }
    ]

    for svc in services:
        print(f"Starting {svc['name']}...")
        try:
            if os.name == 'nt':
                # Use start to create a separate persistent window
                subprocess.Popen(["start", "cmd", "/c"] + svc["command"], shell=True, cwd=svc["cwd"])
            else:
                subprocess.Popen(svc["command"], cwd=svc["cwd"])
            time.sleep(2)
        except Exception as e:
            print(f"Failed to start {svc['name']}: {e}")

    print("\n" + "=" * 50)
    print("ALL SERVICES ARE RUNNING AUTOMATICALLY")
    print("The VAS System is now monitoring in the background.")
    print("=" * 50)

if __name__ == "__main__":
    start_services()
