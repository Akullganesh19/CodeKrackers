## 2025-07-09 — Authentication Cryptography Migration
**Risk identified:** The backend uses `passlib` and `python-jose`. `passlib` is effectively abandoned and incompatible with modern `bcrypt` (>=4.0.0). `python-jose` is unmaintained and superseded by `PyJWT`. This is a high-security risk for future compatibility and vulnerability management.
**Migration target:** Use the standard `bcrypt` library directly for password hashing. Use `PyJWT` for JWT implementation.
**Migrated this session:** Replaced `passlib` with `bcrypt` and `python-jose` with `PyJWT` in `backend/core/security.py` and `backend/core/deps.py`. Updated `backend/requirements.txt`.
**Remaining:** None for this specific slice.
**Next session:** Look for other outdated security dependencies like `python-multipart` or outdated models.
