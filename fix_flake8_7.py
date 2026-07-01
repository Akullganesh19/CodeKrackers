with open("backend/services/ai_deep_scan.py", "r") as f:
    content = f.read()

content = content.replace("                \"content\": \"You are a cybersecurity expert specializing in Vishing and Smishing detection.\",", "                \"content\": \"You are a scam detection expert.\",")
with open("backend/services/ai_deep_scan.py", "w") as f:
    f.write(content)
