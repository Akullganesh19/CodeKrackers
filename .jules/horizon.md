## 2025-02-15 — Authentication Libraries Modernization
**Risk identified:** The backend relies on `passlib` and `python-jose` for password hashing and JWT handling. `passlib` is unmaintained and incompatible with modern versions of the native `bcrypt` library (4.0.0+), causing failures on modern systems. `python-jose` is also largely unmaintained, raising security and compatibility concerns. Both will become increasingly painful to manage.
**Migration target:** Move to the actively maintained `bcrypt` library for password hashing directly and `PyJWT` for JWT handling.
**Migrated this session:** Replaced `passlib[bcrypt]` with `bcrypt` and `python-jose[cryptography]` with `PyJWT` in `requirements.txt`. Updated password hashing (`verify_password`, `get_password_hash`) in `backend/core/security.py` to use `bcrypt` directly. Replaced `jose` imports with `PyJWT` equivalents in `security.py` and `deps.py`.
**Remaining:** The migration of these core dependencies is complete for the backend authentication system.
**Next session:** Look for other unmaintained or lagging dependencies in `requirements.txt` or `package.json`.
