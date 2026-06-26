## 2025-06-26 — Migrate passlib to direct bcrypt
**Risk identified:** The codebase relies on `passlib` for password hashing, which in turn utilizes Python's built-in `crypt` module. The `crypt` module is deprecated in Python 3.11 and completely removed in Python 3.13. Continuing to use `passlib` will introduce critical failures and block upgrading the project to modern Python 3.13 environments, rapidly compounding technical debt.
**Migration target:** Direct use of the standard, actively-maintained `bcrypt` module.
**Migrated this session:** Entirely replaced `passlib.context.CryptContext` with direct `bcrypt.hashpw` and `bcrypt.checkpw` in `backend/core/security.py`, maintaining `rounds=12` compatibility. Removed `passlib` from `backend/requirements.txt` and `api/requirements.txt`.
**Remaining:** No remaining slices. The migration was isolated to `backend/core/security.py` and is complete.
**Next session:** Migration finished.
