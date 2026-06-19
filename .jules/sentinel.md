## 2024-05-20 — Unrestricted User Registration Privilege Escalation

**Attacked:**
- `POST /api/auth/register`
- `POST /api/v1/auth/register`
- `POST /api/users/`
- `POST /api/v1/users/`

**Found:**
The registration endpoints implicitly trusted the user-provided payload for the `role` field. By submitting a payload with `"role": "super_admin"`, an attacker could register a new account and immediately receive the highest privilege level in the system, bypassing all access controls. The `verify_otp` endpoint had the same vulnerability when implicitly creating a new user upon a valid OTP verification.

**Severity:** 🔴 Exploitable now

**Fixed or flagged:**
Fixed. The registration and OTP verification logic in `backend/api/auth.py`, `backend/api/v1/endpoints/auth.py`, `backend/api/users.py`, and `backend/api/v1/endpoints/users.py` was updated to explicitly hardcode the assigned role to `UserRole.citizen` or `UserRole.USER` (or their string representations), disregarding any role supplied in the request body.

**Systemic pattern:**
Implicit trust of client-provided object payloads during creation or updates. Other creation endpoints (like `POST /api/childlock/` or `POST /api/threats/`) should be audited to ensure they do not blindly trust the client-provided input if it contains sensitive fields like `status` or `is_verified`.
