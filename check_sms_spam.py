import re
import sys
import os

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import intelligence layers
from backend.services.ai_deep_scan import ai_deep_scan
from backend.services.openclaw_agent import openclaw_analysis
from backend.services.mythos_engine import forensic_engine

def analyze_message(content):
    # Sanitize for terminal output
    safe_content = content.replace("₹", "Rs.")
    
    print("VAS Intelligence Engine - SMS Analysis")
    print(f"Message: \"{safe_content}\"")
    print("-" * 50)
    
    # 1. AI Deep Scan (Gemma/Groq)
    print("Engaging Local AI Intelligence...")
    ai_result = ai_deep_scan(content)
    
    # 2. OpenMythos Latent Reasoning Layer
    print("Initializing OpenMythos Recurrent-Depth Transformer (16-loop reasoning)...")
    mythos_result = forensic_engine.deep_analyze(content)
    
    # 3. OpenClaw Forensic Layer
    print("Connecting to OpenClaw Autonomous Agent...")
    agent_status = openclaw_analysis(content)
    
    print("\nForensic Analysis Results:")
    print(f"  [!] Primary Engine: {ai_result['reason']}")
    print(f"  [!] OpenMythos RDT: {mythos_result['status']} (Loops: {mythos_result['recurrence_loops']})")
    
    if agent_status:
        print(f"  [+] OpenClaw Agent: ACTIVE (Gateway: {agent_status['gateway']})")
    
    print("-" * 50)
    score = ai_result['score_increase']
    print(f"FINAL THREAT CONFIDENCE: {round(score * 100, 2)}%")
    
    if score >= 0.7:
        print("ACTION: BLOCK (Highly Likely Scam)")
    elif score >= 0.4:
        print("ACTION: FLAG (Suspicious)")
    else:
        print("ACTION: ALLOW (Safe)")

if __name__ == "__main__":
    msg = "IPS Delivery: We have an item for you but are unable to deliver due to an incomplete address. A small redelivery fee of ₹25.00 is required. Update here: https://postal-service-updates.in/track"
    analyze_message(msg)
