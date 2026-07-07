## 2024-07-07 — Backend Security Primitives Migration
**Risk identified:** The backend uses `passlib` for password hashing and `python-jose` for JWTs. Both libraries are currently abandoned by the community and lack active maintenance, presenting an unmanaged security risk in a core security pathway.
**Migration target:** Switch directly to `bcrypt` for password hashing (standard, maintained) and `PyJWT` for JSON Web Tokens (active, standard).
**Migrated this session:** Replaced `passlib` and `python-jose` with `bcrypt` and `PyJWT` in `requirements.txt`, updated `backend/core/security.py` to call bcrypt and jwt APIs directly, and modified `backend/core/deps.py` to catch `jwt.InvalidTokenError`.
**Remaining:** No remaining actions for this specific primitive migration.
**Next session:** Assess other dependency staleness, such as Pydantic v1 to v2 style config classes.
