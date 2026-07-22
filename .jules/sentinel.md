## 2025-02-14 — Authentication Mass Assignment & Crash Vulnerabilities

**Attacked:** User authentication paths (`/api/auth/register`, `/api/auth/verify`) and Password policies.
**Found:**
1. The user models mapped request schemas dynamically upon user creation. Attackers could set their `role` field directly to `admin` during registration and OTP verification, successfully elevating privileges.
2. The authentication endpoints queried for `User.phone_number`, however the ORM defines the field as `User.phone`, causing 500 unhandled errors.
3. The password strength validation enforced a limit of 128 characters while native bcrypt relies on a strict 72-byte limit, presenting a Denial of Service crash. `passlib.context` imported legacy libraries incompatible with Python 3.13.
**Severity:** 🔴 Exploitable now
**Fixed or flagged:** Fixed. Re-routed user creations strictly with `UserRole.CITIZEN`. Handled ORM alignments. Migrated completely to Native Bcrypt and narrowed the byte limit natively to 72. Validated with `test_auth_adversarial.py`.
**Systemic pattern:** Look for `role` schema fields that map dynamically to Pydantic schemas without ignoring input or forcing safe defaults on creation. Watch for schema aliases like `phone_number` and `phone` mismatch.
