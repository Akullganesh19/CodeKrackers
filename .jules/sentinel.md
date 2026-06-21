## 2025-02-28 — [Authentication Brute-Force Bypass via 500 Error]
**Attacked:** The `login` endpoints across the backend which increment `failed_login_attempts` to block brute force attempts.
**Found:** The `failed_login_attempts`, `locked_until`, and `last_login_at` fields were queried and mutated by the backend auth routing but were missing from the underlying SQLAlchemy ORM `User` model. This caused a `500 Internal Server Error` instead of a 401 on failed logins, which aborted the transaction and bypassed the brute-force lockout entirely.
**Severity:** 🔴
**Fixed or flagged:** Fixed. Added missing schema attributes to the SQLAlchemy `User` ORM class so brute force lockouts correctly persist.
**Systemic pattern:** If one ORM model was missing properties that endpoints relied on, it is highly likely that other ORM definitions diverge from their usages or Pydantic counterparts.
