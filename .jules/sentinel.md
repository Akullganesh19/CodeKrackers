## 2024-07-24 — [Auth Role Escalation and ORM Crash]
**Attacked:** `/api/auth/register` and `/api/auth/verify` endpoints.
**Found:**
1. The schemas accepted a `role` field from user input, and the endpoints directly initialized the ORM `User` model with this user-supplied role, allowing any unauthenticated user to register as an `admin` or `super_admin`.
2. When creating or querying the `User` ORM object, the code referred to the phone field as `phone_number`. The actual database column and ORM attribute is `phone`, resulting in an `AttributeError` crashing the endpoint whenever phone numbers were involved.
3. In `/api/auth/verify`, if `redis` is unavailable, it attempted to fallback to an undefined `otp_code` variable, causing a `NameError`.
**Severity:** 🔴 (Exploitable)
**Fixed or flagged:** Fixed. Forced `UserRole.citizen` hardcoded assignment on user creation in both registration and OTP verification paths. Corrected all ORM references from `phone_number` to `phone`. Replaced undefined `otp_code` fallback with `None` to gracefully reject the verification instead of crashing. Added regression tests in `scratch/test_auth.py` verifying the fixes.
**Systemic pattern:** Models exposing Pydantic schemas that are unsafely passed directly into ORM constructors without omitting restricted fields (like `role`, `rbac_level`, `safety_score`, `scams_avoided`).
