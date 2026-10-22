## 2025-05-15 — Unauthenticated Privilege Escalation via User Registration and OTP Verification
**Attacked:** `register_user` and `verify_otp` endpoints in `backend/api/auth.py` and `backend/api/v1/endpoints/auth.py`.
**Found:** The `UserRegister` and `OTPVerify` schemas allow users to send arbitrary values for `role`, which is then blindly accepted and persisted to the database. An attacker can create an account (or log in via OTP) as an "admin" or "super_admin".
**Severity:** 🔴
**Fixed or flagged:** Fixed. Replaced the dynamic role assignment with a hardcoded "citizen" role on creation.
**Systemic pattern:** Any endpoint that uses a broad Pydantic schema for input and blindly maps it to an ORM model without explicit filtering may be vulnerable to mass assignment / privilege escalation. Look for other uses of `role` or `rbac_level` in incoming schemas.
