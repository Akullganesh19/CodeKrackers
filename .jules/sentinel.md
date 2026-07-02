## 2023-10-27 — Auth Endpoint Registration & OTP Vulnerabilities
**Attacked:** User registration (`/api/auth/register`) and OTP verification (`/api/auth/verify`) in `backend/api/auth.py`.
**Found:**
1. **Role Escalation during Registration**: A user could provide `"role": "super_admin"` in the `UserRegister` JSON payload, which was blindly mapped to the `UserRole` enum and saved, granting them instant super admin privileges.
2. **500 Server Error on Registration with Phone**: Supplying a `phone_number` caused an ORM crash because the `User` model expects the field `phone`, not `phone_number`.
3. **500 Server Error on OTP Verification (Redis Offline)**: The fallback mechanism when Redis was offline incorrectly mapped to a local undeclared variable `otp_code` instead of failing gracefully, causing an exception when `code` verification was attempted against an undefined variable.
**Severity:** 🔴 (Role Escalation) / 🔴 (500 DoS Crash on Registration) / 🟡 (500 Error when Redis Offline)
**Fixed or flagged:** Fixed.
- Hardcoded `UserRole.CITIZEN` upon user creation in both `register_user` and `verify_otp` functions.
- Updated `phone_number` mapping to explicitly map to the `phone` field in the ORM.
- Updated Redis fallback to correctly set `stored_code` to `None` if `redis_client` is unavailable, correctly triggering the 400 invalid OTP response.
**Systemic pattern:** Mass assignment privilege escalation vulnerability during user creation. Look for other endpoints (e.g., PUT /users or PATCH /profile) that might blindly map Pydantic schema fields into SQLAlchemy models without dropping protected fields like `role` or `is_active`.
