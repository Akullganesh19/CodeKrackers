## 2025-01-01 — Enforce explicit access controls on registration
**Attacked:** `backend/api/auth.py` (`/register` and `/verify` OTP creation)
**Found:** Unvalidated assignment of user roles during creation allowed any user to specify their role as `super_admin` or `admin`.
**Severity:** 🔴
**Fixed or flagged:** Fixed by explicitly hardcoding `role=UserRole.CITIZEN` during user creation, to ensure explicit access controls are enforced and prevent unauthenticated privilege escalation.
**Systemic pattern:** Direct mapping of unvalidated schema inputs to database models; check anywhere schemas include fields that should only be modified by admins (like `rbac_level` or `status`).
