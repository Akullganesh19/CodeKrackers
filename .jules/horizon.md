## 2024-10-12 — JWT and Password Hashing Migration
**Risk identified:** `passlib` is abandoned and incompatible with modern bcrypt versions, and `python-jose` is unmaintained. Both present significant future migration and security risks as their ecosystems drift.
**Migration target:** Use `bcrypt` directly for password hashing and `PyJWT` for JWT signing and validation.
**Migrated this session:** Replaced `passlib` and `python-jose` with `bcrypt` and `PyJWT` in `backend/core/security.py` and `backend/core/deps.py`, including requirements update.
**Remaining:** None for this specific slice, though further verification across broader services if they directly used these packages might be necessary.
**Next session:** Look for other deprecated patterns or unmaintained libraries to migrate.
