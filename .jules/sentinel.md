
## 2025-05-18 — Auth Privilege Escalation & Bypass Risks
**Attacked:** Registration, Login, and OTP Verification code paths (`backend/api/auth.py`, `backend/models/orm.py`)
**Found:**
1. **Mass Assignment Privilege Escalation**: The `UserRegister` and `OTPVerify` schemas accepted a `role` field directly from client payloads without sanitization. An attacker could register or login via OTP providing `"role": "super_admin"` to gain total control over the system.
2. **Missing ORM Fields**: The `failed_login_attempts` and `locked_until` properties were used by brute-force protection logic dynamically but didn't exist on the `User` model (`backend/models/orm.py`), causing them to be lost upon any database query and rendering lockout protections useless.
3. **Invalid Attribute Crash**: A bug in OTP verify and registration paths referenced `User.phone_number`, which crashed the API because the ORM field is `phone`.
4. **OTP Redis Bypass**: A mock fallback during Redis downtime returned the local variable `otp_code` directly. Because `otp_code` wasn't even initialized in `verify_otp`, this would either crash or inadvertently allow any provided OTP code through.
**Severity:** 🔴 Exploitable now
**Fixed or flagged:** Fixed. Schemas stripped of `role` fields, default role hardcoded to `UserRole.CITIZEN`. Fields properly added to ORM schema. References fixed to `User.phone`. OTP Redis failure logic refactored to fail-closed returning `None`.
**Systemic pattern:** Look for `BaseModel` schemas mapped straight to models for creation/updates without validating restricted properties, particularly in `auth.py` and `users.py` related endpoints.
