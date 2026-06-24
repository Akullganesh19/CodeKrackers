## 2025-06-25 — Passlib to Bcrypt Migration
**Risk identified:** The backend authentication system was using `passlib[bcrypt]` for password hashing. Passlib is effectively abandoned by its maintainers and will cause major compatibility issues with Python 3.13 due to its reliance on the deprecated `crypt` module. This is a severe future-proofing risk as the ecosystem moves to newer Python versions.
**Migration target:** Raw `bcrypt` directly, eliminating the unnecessary intermediate abstraction layer of `passlib` and avoiding the Python 3.13 breaking change.
**Migrated this session:**
- Replaced `passlib[bcrypt]` with `bcrypt==4.0.1` in `backend/requirements.txt`
- Refactored `verify_password` and `get_password_hash` in `backend/core/security.py` to use `bcrypt.checkpw` and `bcrypt.hashpw` directly instead of `CryptContext`.
**Remaining:** None for this specific migration piece. The codebase now natively uses `bcrypt` without `passlib`.
**Next session:** Look for other deprecated dependencies, such as potentially moving from `python-jose` to `pyjwt` if similar abandonment risks exist.
