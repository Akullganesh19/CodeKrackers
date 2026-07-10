## 2025-06-25 — Passlib and python-jose replacement
**Risk identified:** The backend relies on `passlib` for password hashing and `python-jose` for JWT tokens. `passlib` is unmaintained and causes compatibility issues with modern bcrypt (>= 4.0.0). `python-jose` is also largely unmaintained, creating a security and reliability risk.
**Migration target:** The modern ecosystem standard is to use the `bcrypt` library directly for password hashing and `PyJWT` for JWT encoding/decoding.
**Migrated this session:**
- Removed `passlib[bcrypt]` and `python-jose[cryptography]` from `backend/requirements.txt`.
- Added `bcrypt` and `PyJWT` to `backend/requirements.txt`.
- Refactored `backend/core/security.py` to use `bcrypt.hashpw` and `bcrypt.checkpw` directly.
- Updated password limits from 128 to 72 characters in `backend/core/security.py` and `backend/schemas/user.py` to comply with bcrypt's internal byte limits.
- Updated `backend/core/deps.py` to handle `jwt.InvalidTokenError` instead of `jose.JWTError`.
**Remaining:** The migration of backend core security dependencies is fully complete.
**Next session:** Look for outdated async dependencies or unstructured `print`/`logger` paradigms that can be updated to structural logging.
