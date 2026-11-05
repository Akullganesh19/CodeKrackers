## 2025-02-23 — Migrate python-jose and passlib to PyJWT and bcrypt
**Risk identified:** `python-jose` and `passlib` are unmaintained legacy libraries, increasing technical debt and risk of unpatched vulnerabilities.
**Migration target:** The ecosystem is moving toward `PyJWT` for JWT generation/validation and using `bcrypt` directly for password hashing.
**Migrated this session:** Replaced `python-jose` with `PyJWT` and `passlib` with `bcrypt` in `backend/core/security.py` and `backend/core/deps.py`, updating all requirement files.
**Remaining:** No remaining pieces for this specific JWT/password hashing migration.
**Next session:** Assess other potential legacy libraries for replacement.
