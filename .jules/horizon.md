## 2025-06-30 — Passlib to Bcrypt Migration
**Risk identified:** The `passlib` library is unmaintained and causes deprecation warnings and errors in Python 3.13 due to its reliance on the standard library `crypt` module (which was removed in Python 3.13 via PEP 594).
**Migration target:** Move to using `bcrypt` directly for password hashing.
**Migrated this session:** Migrated `verify_password` and `get_password_hash` in `backend/core/security.py` to use `bcrypt` directly. Removed `passlib` from the dependency files `backend/requirements.txt` and `api/requirements.txt`.
**Remaining:** N/A (The core security logic is migrated)
**Next session:** N/A
