import subprocess

subprocess.run("autoflake --in-place --remove-all-unused-imports --remove-unused-variables -r backend/", shell=True)
subprocess.run("black backend/", shell=True)
