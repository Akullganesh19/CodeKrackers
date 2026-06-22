## 2024-05-18 — [Fixed Concurrency Bug in Spam Shield Auto-Blacklist]
**Value type:** Report Count & Confidence Score for Threat Signatures
**Drift risk found:** The `auto_blacklist` function used a non-atomic read-modify-write pattern on `BlacklistEntry.report_count` and `BlacklistEntry.confidence`. If multiple identical threat signals arrived concurrently, they'd read the same database state and overwrite each other, causing missed counts.
**Fix:** Refactored to an atomic `UPDATE` expression using SQLAlchemy `update` paired with a conditional `case` statement to enforce the 1.0 confidence cap atomically. Added fallback `try...except` block using `db.begin_nested()` to gracefully handle race conditions on initial `INSERT` constraints.
**Proven by:** Created `backend/tests/services/test_threat_intel_concurrency.py` which spawns 10 threads simulating concurrent scam reports. It correctly proves that all 11 reports (1 initial + 10 threads) increment the count to exactly 11 without drifting.
**Other balances to check:** `safety_score` increment in `restore_user_safety_scores` (tasks.py), `access_count` in `trigger_canary` (canary_service.py).
