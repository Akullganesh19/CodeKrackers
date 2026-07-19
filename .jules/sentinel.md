## 2025-10-24 — [Mass Assignment Privilege Escalation in Authentication]
**Attacked:** User registration (`/api/auth/register`) and OTP verification (`/api/auth/verify`) endpoints in `backend/api/auth.py`.
**Found:** The request schemas allowed arbitrary strings for the `role` parameter. The backend directly instantiated new User objects using `UserRole(user_in.role)` and `UserRole(otp_verify.role)`, allowing an attacker to inject `"super_admin"` or `"admin"` and permanently escalate privileges upon creation.
**Severity:** 🔴
**Fixed or flagged:** Fixed by explicitly overriding client input and hardcoding `role=UserRole.CITIZEN` during user instantiation.
**Systemic pattern:** Search for endpoints creating resources based on client-provided models containing sensitive fields (like `role`, `rbac_level`, `safety_score`) that are blindly mapped directly to the ORM instances without exclusion or overrides.
