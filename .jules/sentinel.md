## 2026-05-08 — Privilege Escalation in User Registration
**Attacked:** Auth registration and OTP verification endpoints (`/api/auth/register`, `/api/auth/verify`)
**Found:** Users could pass `role: admin` or `role: super_admin` in the payload and be directly granted administrative privileges without validation.
**Severity:** 🔴
**Fixed or flagged:** Fixed. Ignored the user-provided role in the payload and forced the `UserRole.CITIZEN` default upon creation.
**Systemic pattern:** Blindly trusting client payloads in data creation (Mass Assignment). Look for similar vulnerabilities in update endpoints (e.g., `/api/users/update`).
