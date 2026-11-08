## 2026-11-07 — Unauthenticated Mass Assignment in Registration
**Attacked:** User Registration Endpoint (`/api/auth/register`)
**Found:** Unvalidated `role` field mapped directly to SQLAlchemy `User` model, allowing privilege escalation.
**Severity:** 🔴
**Fixed or flagged:** Fixed. Replaced dynamic assignment with hardcoded `UserRole.CITIZEN` and added regression test.
**Systemic pattern:** Check other endpoints that use `User(**schema.model_dump())` or map inputs to DB models without stripping sensitive fields.
