## 2025-06-27 — Passlib to Bcrypt Migration
**Risk identified:** The `passlib` library relies on Python's built-in `crypt` module which is deprecated and removed in Python 3.13. Waiting to migrate would result in unexpected deployment failures or broken authentication when upgrading Python versions.
**Migration target:** Direct use of the `bcrypt` library (version 4.0.1) replacing `passlib.context.CryptContext` for password hashing and verification.
**Migrated this session:** Replaced `passlib[bcrypt]` with `bcrypt==4.0.1` in `backend/requirements.txt`. Refactored `backend/core/security.py` to use `bcrypt.hashpw` and `bcrypt.checkpw` instead of `CryptContext`.
**Remaining:** No further migrations needed for `passlib` in backend.
**Next session:** Start looking for other legacy frameworks or patterns (e.g., outdated dependency versionings, deprecated API endpoints).
