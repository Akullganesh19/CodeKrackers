## 2024-05-24 — Mass Assignment Vulnerability in Auth

**Attacked:** User registration and OTP creation API endpoints (`/api/auth/register`, `/api/auth/verify`).
**Found:** Mass assignment privilege escalation vulnerability. A malicious actor could inject arbitrary roles (such as `"role": "admin"`) directly from the request payload during both account registration (`UserRegister` model) and OTP verification (`OTPVerify` model), which the backend blindly trusted and used when creating new database records.
**Severity:** 🔴 Exploitable now
**Fixed or flagged:** Fixed. Modified the endpoints to ignore client-provided roles entirely and explicitly hardcode `UserRole.CITIZEN` during user creation, successfully eliminating the vulnerability without negatively impacting standard flows. Additionally, added `backend/test_auth_sentinel.py` as an adversarial regression test to prevent recurrence.
**Systemic pattern:** Developers should review Pydantic schemas in other areas (e.g. `UserUpdate`) to ensure restricted fields (`role`, `is_active`, `safety_score`) are not exposed for write operations without appropriate authorization checks, preventing tampering.
