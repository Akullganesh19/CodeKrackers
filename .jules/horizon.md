## 2025-02-27 — Migrate passlib and python-jose to bcrypt and PyJWT
**Risk identified:** The Python backend was using `passlib` for password hashing and `python-jose` for JWT tokens. Both libraries are unmaintained (abandonware) and have incompatibility issues with modern dependencies (e.g., `passlib` fails with `bcrypt` 4.0.0+). This represents a compounding security risk and technical debt.
**Migration target:** Modern, actively maintained security primitives. Using the native `bcrypt` library directly for password hashing and `PyJWT` for robust JWT token generation and validation.
**Migrated this session:**
- Replaced `passlib[bcrypt]` with `bcrypt` in `backend/requirements.txt`.
- Replaced `python-jose[cryptography]` with `PyJWT` in `backend/requirements.txt`.
- Migrated password hashing mechanisms in `backend/core/security.py` to use `bcrypt.hashpw` and `bcrypt.checkpw`.
- Migrated JWT logic in `backend/core/security.py` and `backend/core/deps.py` to use `import jwt` and `jwt.InvalidTokenError` from PyJWT.
**Remaining:** The migration of these two specific dependencies is fully complete for the backend module.
**Next session:** Look for outdated or unmaintained frontend dependencies (e.g., legacy Next.js patterns) or further backend dependency upgrades.
