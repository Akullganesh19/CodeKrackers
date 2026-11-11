## 2024-05-20 — Authentication and Authorization bypass
**Attacked:** `backend/api/auth.py` and `backend/api/v1/endpoints/auth.py` (OTP verification and Registration)
**Found:**
1. `NameError` crash in `verify_otp` fallback (`otp_code` is undefined) when redis is down, and dangerous mock pass.
2. Mass Assignment vulnerability in both `/register` and `/verify` allowing users to set any role (e.g. `super_admin`) during account creation.
**Severity:** 🔴
**Fixed or flagged:** Fixed. Replaced undefined mock `otp_code` fallback with `None` to prevent crash and bypass. Hardcoded `UserRole.CITIZEN` or `UserRole.citizen` for new user creation across `auth.py` and `v1/endpoints/auth.py` to prevent privilege escalation.
**Systemic pattern:** Unvalidated assignment of `role` fields directly from user input payloads. Other endpoints accepting user roles should be checked.
