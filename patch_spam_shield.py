import re

with open('backend/services/spam_shield.py', 'r') as f:
    content = f.read()

search_str = """    # ── Decision ──
    spam_score = min(spam_score, 1.0)
    threshold: float = user_filter.min_spam_score_to_block if user_filter else 0.7"""

replace_str = """    # ── Decision ──
    spam_score = min(spam_score, 1.0)
    threshold: float = user_filter.min_spam_score_to_block if user_filter else 0.7

    # ── Synapse: Cross-System Intelligence ──
    # If the user has a low safety score, dynamically lower the block threshold
    user_record = db.query(User).filter(User.id == user_id).first()
    if user_record and hasattr(user_record, "safety_score") and user_record.safety_score < 70.0:
        threshold = max(0.4, threshold - 0.15)
        breakdown.append({"factor": f"User safety score low ({user_record.safety_score:.0f}/100) — stricter blocking applied", "points": "-0.15 threshold", "type": "negative"})"""

if search_str in content:
    content = content.replace(search_str, replace_str)
else:
    print("WARNING: Replacement string not found in spam_shield.py")

with open('backend/services/spam_shield.py', 'w') as f:
    f.write(content)
