## 2025-06-25 — Privilege Escalation / Mass Assignment via Registration and OTP

**Attacked:** The user registration (`/register`) and OTP verification (`/verify`) paths in `backend/api/auth.py` and `backend/api/v1/endpoints/auth.py`.

**Found:** The `UserRegister` and `OTPVerify` Pydantic schemas included `role` in their payload. Because this value was mapped directly into the new `User` object upon creation, an attacker could supply `"role": "super_admin"` during registration or OTP verification. This resulted in the creation of a user with elevated system privileges (a severe, exploitable vulnerability).

**Severity:** 🔴 Exploitable now

**Fixed or flagged:** Fixed. Explicitly ignored the `role` field from the request payload during user creation in both `register_user` and `verify_otp` handlers. Hardcoded the role to `UserRole("citizen")` or `"citizen"` respectively.

**Systemic pattern:** Mass assignment / unchecked payload mapping. We should look for any other `POST` or `PUT` endpoints that take a Pydantic schema and map it blindly to an ORM model without excluding sensitive fields such as `role`, `is_active`, `balance`, `permissions`, etc.
