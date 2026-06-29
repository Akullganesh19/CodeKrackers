## 2024-05-24 — Sentinel findings

**Attacked:** User registration and OTP creation API endpoints (`/api/auth/register`, `/api/auth/verify`).
**Found:** Mass assignment privilege escalation vulnerability. The user was able to inject arbitrary roles (such as `"role": "admin"`) directly from the request payload during both account registration (`UserRegister` model) and OTP verification (`OTPVerify` model), which the backend blindly trusted and used when creating new records.
**Severity:** 🔴 Exploitable now
**Fixed or flagged:** Fixed. The endpoints now ignore client-provided roles entirely and explicitly hardcode `UserRole.CITIZEN` upon creation, successfully eliminating the vulnerability without negatively impacting standard flows. Added `backend/test_auth_sentinel.py` to prevent regression.
**Systemic pattern:** Ensure Pydantic schemas in other areas (e.g. `UserUpdate`) do not expose restricted fields (`role`, `is_active`, `safety_score`) without appropriate authorization checks, preventing user data tampering.
