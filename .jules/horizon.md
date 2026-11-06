## 2023-11-20 — Passlib and python-jose removal
**Risk identified:** `passlib` is unmaintained and incompatible with newer versions of `bcrypt`. `python-jose` is also unmaintained and failing to support newer Python versions and cryptography changes.
**Migration target:** Use `bcrypt` directly for password hashing and `PyJWT` for JWT generation/validation.
**Migrated this session:** Migrated `backend/core/security.py`, `backend/core/deps.py`, and requirements to remove `passlib` and `python-jose` and utilize `bcrypt` and `PyJWT`.
**Remaining:**
**Next session:** Complete.
