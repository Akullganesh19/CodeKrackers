## 2024-05-23 — Atomic Update for Safety Score

**Value type:** User safety score
**Drift risk found:** Read-modify-write gap inside `restore_user_safety_scores` (`backend/tasks.py`) that could result in lost updates if the score is modified concurrently by another process or API call between the `select` and the `commit`.
**Fix:** Changed to an atomic update using SQLAlchemy's `update()` statement (`update(User).where(User.id == user.id).values(safety_score=case((new_score > 100.0, 100.0), else_=new_score))`).
**Proven by:** Simulated concurrent updates to safety score during restoration (`backend/test_safety_score_concurrency.py`).
**Other balances to check:** `report_count` inside `backend/services/threat_intel.py`.

## 2024-05-23 — Atomic Update for Blacklist Report Count

**Value type:** Blacklist `report_count` and `confidence`
**Drift risk found:** Read-modify-write gap in `auto_blacklist` (`backend/services/threat_intel.py`) which updates the report count and confidence of an existing entry. This could lead to dropped reports during concurrent execution.
**Fix:** Converted the Python-level increment into an atomic database `update()` query using SQLAlchemy (`update(BlacklistEntry).where(BlacklistEntry.id == existing.id).values(report_count=BlacklistEntry.report_count + 1, confidence=case((new_confidence > 1.0, 1.0), else_=new_confidence))`).
**Proven by:** Concurrency test added to `backend/test_blacklist_concurrency.py`.
**Other balances to check:** The `access_count` in `backend/services/canary_service.py`.
