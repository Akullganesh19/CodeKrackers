## 🛡️ Adversarial Verification Report

**Scope attacked:** Auth & Brute-Force Rate Limiting (login/OTP)

**🔴 Exploitable findings:**
- **Crash on Failed Login:** `failed_login_attempts`, `locked_until`, and `last_login_at` were hardcoded into endpoint logic in `api/auth.py` and `api/login.py`, but were completely missing from the actual SQLAlchemy `User` model (`models/orm.py`). Thus, every failed login crashed the app with an `AttributeError` returning HTTP 500. This caused the transaction to roll back, meaning no `failed_login_attempts` were ever tracked in the database, allowing an infinite bypass of brute-force protection.
- **Reproduction:** Attempt to login with the wrong password. Observe HTTP 500 rather than HTTP 401.

**🟡 Latent findings:**
- **Race Condition in Brute Force Tracking:** `failed_login_attempts` is updated non-atomically in Python (`u.failed_login_attempts = u.failed_login_attempts + 1`). If a user spams 5 failed logins concurrently, the value will only increment to `1` because all requests read `0` simultaneously, drastically extending the number of allowed brute force attempts. Fix direction: Use `User.failed_login_attempts = User.failed_login_attempts + 1` via `update(User)` atomically.

**🟢 Theoretical findings:**
- None in this cycle.

**Fixed this session:**
- Added `failed_login_attempts`, `locked_until`, and `last_login_at` to `backend/models/orm.py` to fix the 500 error and actually track brute-force failures. Added columns to sqlite DB `vsdp.db`. `pytest` regression checks confirm the app runs correctly.

**Requires human review:**
- Review the atomic concurrency issue for `failed_login_attempts`.

## YYYY-MM-DD — [Brute Force Missing Columns]
**Attacked:** Login / OTP verify boundaries (`api/auth.py`, `api/login.py`)
**Found:** `failed_login_attempts`, `locked_until`, `last_login_at` fields were missing in `models/orm.py`. Any failed login threw an AttributeError (500) and failed to track brute-force attempts.
**Severity:** 🔴
**Fixed or flagged:** Fixed. Added the columns to the DB Model and actual SQLite DB.
**Systemic pattern:** Look for features implemented in Endpoints that assume attributes on Models that were never actually added to `models/orm.py`.
