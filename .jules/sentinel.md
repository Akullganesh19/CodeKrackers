## 2026-05-08 — Privilege Escalation in User Registration
**Attacked:** `backend/api/auth.py` -> `register_user` and `verify_otp`
**Found:** Mass assignment vulnerability where the client could pass `role: "super_admin"` in the JSON payload, and it was blindly passed into the `User` object creation via `UserRole(user_in.role)` and `UserRole(otp_verify.role)`. Additionally found and fixed 500 crashes occurring because of a `.phone` vs `.phone_number` DB column mismatch, and missing `hashed_password` initialization during OTP signups.
**Severity:** 🔴
**Fixed or flagged:** Fixed. Hardcoded `UserRole.CITIZEN` in both endpoints. Updated `User` model instantiation to properly populate the required `phone` and `hashed_password` fields (generating a dummy randomized secure hash for OTP users).
**Systemic pattern:** If one endpoint had mass assignment, others might too. Any object initialization directly taking properties from user input payloads should be audited across the API, especially for roles, permissions, scopes, and balances.
