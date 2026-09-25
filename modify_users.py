import re

with open("backend/api/users.py", "r") as f:
    content = f.read()

# Add import if not present
if "from backend.models.orm import ScoreHistory" not in content:
    content = content.replace("from backend.models import User, UserRole", "from backend.models import User, UserRole\nfrom backend.models.orm import ScoreHistory")

# Add endpoint
endpoint = """
@router.get("/me/score-history")
async def get_score_history(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    \"\"\"Get current user's safety score history.\"\"\"
    result = await db.execute(
        select(ScoreHistory).where(ScoreHistory.user_id == current_user.id).order_by(ScoreHistory.recorded_at.desc())
    )
    history = result.scalars().all()

    return [
        {
            "id": str(h.id),
            "score": h.score,
            "recorded_at": h.recorded_at.isoformat() if h.recorded_at else None
        }
        for h in history
    ]
"""

if "@router.get(\"/me/score-history\")" not in content:
    content = content + "\n" + endpoint

with open("backend/api/users.py", "w") as f:
    f.write(content)
print("Updated users.py")
