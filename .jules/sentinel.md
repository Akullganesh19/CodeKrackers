## 2024-05-24 — Unauthenticated Mass Assignment of Roles

**Attacked:** `POST /api/v1/auth/register` and `POST /api/v1/auth/verify`
**Found:** An attacker can elevate privileges to `super_admin` or `admin` during registration or OTP verification by passing `"role": "super_admin"` in the JSON body. The API blindly maps `UserRole(user_in.role)` directly into the database model without checking permissions.
**Severity:** 🔴
**Fixed or flagged:** Fixed. I explicitly hardcoded the role to `UserRole.CITIZEN` upon registration, forcing the role upgrade to be handled by a separate, protected admin route.
**Systemic pattern:** Unvalidated input parameters mapped directly to SQLAlchemy schemas. Other creation and update routes should be checked for mass assignment vulnerabilities.
