## 2023-10-27 — Auth Privilege Escalation via Mass Assignment
**Attacked:** POST /api/v1/auth/register and POST /api/v1/auth/verify
**Found:** Pydantic models `UserRegister` and `OTPVerify` accept `role` field. Endpoints blindly assign this value to newly created users, allowing any user to register as `super_admin`. Also found `NameError` crash in `verify_otp` when Redis is down, and an ORM mapping crash (`User.phone_number` vs `User.phone`) completely breaking OTP verification.
**Severity:** 🔴 Exploitable now (Privilege escalation)
**Fixed or flagged:** Fixed. Removed `role` from Pydantic schemas, securely hardcoded `UserRole.citizen` on user creation, fixed fallback logic if Redis is down, and fixed the ORM property mapping bug.
**Systemic pattern:** Look for Pydantic models in other endpoints accepting sensitive fields (e.g. `is_active`, `rbac_level`, `safety_score`) and trusting client input for database updates.
