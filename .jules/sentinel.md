## 2024-05-18 — Unbound Variable `otp_code` Causes Bypass or Server Crash
**Attacked:** OTP Verification (`/verify` endpoint in `backend/api/auth.py`)
**Found:** The `verify_otp` function references `otp_code` which is not defined in scope if `redis_client` is missing. When Redis is down (e.g. `redis_client` is None), `stored_code = redis_client.get(redis_key) if redis_client else otp_code` is executed. `otp_code` is defined in `send_otp` but not in `verify_otp`. In Python, this will raise an `UnboundLocalError` or `NameError` causing a 500 crash. Or, if `otp_code` somehow ends up being an empty string (or if we imagine it leaks), it could lead to auth bypass. Most critically, it crashes the endpoint when Redis is unavailable, instead of cleanly rejecting. More over, `redis_client.get(...)` could return string when `otp_verify.code` could be string, but if `otp_code` was not defined it's a direct failure. Wait, since it's an UnboundLocalError, an attacker sending any request when Redis is down results in a 500 error instead of a 400 or rejecting properly, which means the fallback is totally broken.
**Severity:** 🔴
**Fixed or flagged:** Flagged for fix. (And will fix).
**Systemic pattern:** Poorly tested fallback paths for external services.

## 2024-05-18 — Login Endpoint Concurrency Race Condition for Rate Limiting / Lockout
**Attacked:** Login/OTP failed attempts counter in `backend/api/auth.py`
**Found:** `user.failed_login_attempts += 1` is non-atomic. Two concurrent failed requests could read the same value, increment it, and write it back, skipping a failed attempt count and delaying lockout.
**Severity:** 🟡
**Fixed or flagged:** Flagged. Requires `user.failed_login_attempts = User.failed_login_attempts + 1` in SQL or row-level locking.

## 2024-05-18 — Arbitrary Role Assignment in OTP Registration
**Attacked:** `verify_otp` creates a new user if one doesn't exist.
**Found:** `role=UserRole(otp_verify.role)` allows any unauthenticated user to register as any role (e.g., `admin`) just by providing `role="admin"` in the OTP payload when the user doesn't exist yet!
**Severity:** 🔴
**Fixed or flagged:** Flagged for fix. Will force default role (e.g. `citizen`) or properly validate role assignment based on context.
**Systemic pattern:** Trusting client-provided data for privileged fields on creation.
