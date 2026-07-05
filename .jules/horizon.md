## 2025-07-05 — passlib and python-jose to bcrypt and PyJWT
**Risk identified:** The backend authentication flow was using `passlib[bcrypt]` and `python-jose[cryptography]`. `passlib` is an abandoned library that fails to work with modern bcrypt versions (>=4.0.0), posing a high risk for compilation issues and security risks over time. `python-jose` is similarly unmaintained and increasingly lagging behind in the Python security ecosystem.
**Migration target:** The modern standard is to use `bcrypt` directly for password hashing and verification, and `PyJWT` for decoding and encoding JWT tokens.
**Migrated this session:**
- Updated `backend/requirements.txt` to remove `passlib[bcrypt]` and `python-jose[cryptography]` and replaced them with `bcrypt` and `PyJWT`.
- Updated `backend/core/security.py` to use `bcrypt` and `jwt` directly, replacing `CryptContext` from `passlib`. Exception handling and utf-8 encoding were included.
- Updated `backend/core/deps.py` to use `jwt.InvalidTokenError` in place of `JWTError` from `jose`.
**Remaining:** No further migration needed for this specific dependency swap.
**Next session:** Look into modernizing background task scheduling or the deployment approach for AI models.
