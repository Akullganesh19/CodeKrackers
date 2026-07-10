import asyncio  # noqa: F401
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from .core.database import AsyncSessionLocal
from .services.evidence_chain import EvidenceChain
from .models.orm import Threat, ScoreHistory, User, FIR, HoneypotSession

async def verify_all_evidence_chains():  # noqa: E302
    """
    Background task to automatically verify the integrity of all evidence chains.
    Intended to run once a day to detect any unauthorized tampering with the forensic ledger.  # noqa: E501
    """
    async with AsyncSessionLocal() as db:
        ledger = EvidenceChain(db)
          # noqa: W293
        # Fetch all threat IDs that have an evidence hash (indicating an audit trail exists)  # noqa: E501
        result = await db.execute(
            select(Threat.id).where(Threat.evidence_hash.isnot(None))
        )
        threat_ids = result.scalars().all()
          # noqa: W293
        report = {
            "total_chains_checked": len(threat_ids),
            "tampered_chains": [],
            "timestamp": datetime.utcnow().isoformat()
        }
          # noqa: W293
        for threat_id in threat_ids:
            verification = await ledger.verify_integrity(threat_id)
            if not verification["valid"]:
                report["tampered_chains"].append({
                    "threat_id": str(threat_id),
                    "reason": verification.get("reason"),
                    "block_index": verification.get("block_index")
                })
          # noqa: W293
        # Log the audit results
        if report["tampered_chains"]:
            print(f"CRITICAL: Integrity Audit detected tampering: {report}")
        else:
            print(f"Daily Integrity Audit Complete: All {len(threat_ids)} chains verified.")  # noqa: E501
          # noqa: W293
        return report

async def record_daily_safety_scores():  # noqa: E302
    """
    Snapshots current safety scores for all active users into the ScoreHistory table.
    """
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.is_active == True))  # noqa: E712
        users = result.scalars().all()
          # noqa: W293
        for user in users:
            entry = ScoreHistory(user_id=user.id, score=user.safety_score)
            db.add(entry)
          # noqa: W293
        await db.commit()
        print(f"Recorded daily safety scores for {len(users)} users.")

async def restore_user_safety_scores():  # noqa: E302
    """
    Background task to reward users with no recent activity.
    Restores points to the safety score if no threats were detected in the last 24 hours.  # noqa: E501
    Users who proactively participate in defense (FIRs, Honeypots) receive higher rewards.  # noqa: E501
    """
    async with AsyncSessionLocal() as db:
        # Threshold for "recent" threats
        yesterday = datetime.utcnow() - timedelta(days=1)
          # noqa: W293
        # Subquery to find users who HAD threats recently
        recent_threats_subquery = select(Threat.user_id).where(Threat.detected_at >= yesterday).scalar_subquery()  # noqa: E501
          # noqa: W293
        # Select users who are active, below max score, and NOT in the recent threats list  # noqa: E501
        stmt = select(User).where(
            User.is_active == True,  # noqa: E712
            User.safety_score < 100.0,
            ~User.id.in_(recent_threats_subquery)
        )
          # noqa: W293
        result = await db.execute(stmt)
        users_to_restore = result.scalars().all()

        # Pre-fetch bonuses in bulk to avoid N+1 query problems
        user_ids = [u.id for u in users_to_restore]
          # noqa: W293
        # Users with at least one FIR
        fir_users_stmt = select(FIR.user_id).where(FIR.user_id.in_(user_ids)).distinct()
        fir_users = set((await db.execute(fir_users_stmt)).scalars().all())

        # Users with completed honeypots
        hp_users_stmt = select(Threat.user_id).join(HoneypotSession, HoneypotSession.threat_id == Threat.id)\  # noqa: E501,E999
            .where(Threat.user_id.in_(user_ids), HoneypotSession.status == 'completed').distinct()  # noqa: E501
        hp_users = set((await db.execute(hp_users_stmt)).scalars().all())

        for user in users_to_restore:
            # Base restoration amount
            restoration_points = 2.0

            # FIR Bonus: Reward users for formal reporting (+1.5 points)
            if user.id in fir_users:
                restoration_points += 1.5

            # Honeypot Bonus: Reward users for active intelligence gathering (+2.5 points)  # noqa: E501
            if user.id in hp_users:
                restoration_points += 2.5
              # noqa: W293
            user.safety_score = min(100.0, user.safety_score + restoration_points)
              # noqa: W293
        await db.commit()
        print(f"Daily Score Restoration: Processed {len(users_to_restore)} users.")

async def is_score_protected(db: AsyncSession, user_id: str) -> bool:  # noqa: E302
    """
    Checks if a user has successfully completed a Honeypot session in the last 48 hours.
    Used to prevent point deductions for proactive defenders.
    """
    # Threshold: 48 hours ago
    protection_window = datetime.utcnow() - timedelta(hours=48)
      # noqa: W293
    # Check for completed honeypot sessions linked to the user's threats
    stmt = select(func.count(HoneypotSession.id))\
        .join(Threat, HoneypotSession.threat_id == Threat.id)\
        .where(
            Threat.user_id == user_id,
            HoneypotSession.status == 'completed',
            HoneypotSession.session_end >= protection_window
        )
      # noqa: W293
    result = await db.execute(stmt)
    return (result.scalar() or 0) > 0  # noqa: W292
