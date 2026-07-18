## 2024-05-24 — Privilege Escalation via Mass-Assignment in Auth Registration
**Attacked:** `register_user`, `verify_otp`, `send_otp` in `backend/api/auth.py`
**Found:** A user can pass an arbitrary role (e.g., `role: "super_admin"`) in the JSON payload, which the endpoint directly assigns without validation.
**Severity:** 🔴
**Fixed or flagged:** Fixed. Removed the `role` field from the Pydantic schemas and hardcoded `UserRole.CITIZEN` upon creation.
**Systemic pattern:** Anywhere Pydantic models map 1-to-1 with ORM models and receive user input.

## 2024-05-24 — Server Crash on Failed Login / Brute Force Mitigation
**Attacked:** `login_access_token_password` and `verify_otp` in `backend/api/auth.py`
**Found:** The brute-force protection logic references `user.locked_until` and `user.failed_login_attempts`. These columns were never defined on the `User` ORM model, leading to an immediate 500 error (`AttributeError: 'User' object has no attribute 'locked_until'`) whenever an incorrect password or locked account was evaluated.
**Severity:** 🔴
**Fixed or flagged:** Fixed. Added the missing columns to the `User` model in `backend/models/orm.py`.
**Systemic pattern:** Brute-force protection was added to endpoints but not synced with the database schema.
