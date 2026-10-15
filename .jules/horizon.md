## 2025-02-27 — Migrating away from passlib and python-jose
**Risk identified:** The backend uses `passlib` (abandoned and incompatible with modern `bcrypt` versions > 4.0) and `python-jose` (abandoned and unmaintained, posing security risks).
**Migration target:** The modern ecosystem standard is to use the `bcrypt` library directly for password hashing and verification, and `PyJWT` for JWT signing and validation. Both are actively maintained and compatible with modern Python features.
**Migrated this session:**
- Replaced `passlib[bcrypt]` with `bcrypt` in `backend/requirements.txt`
- Replaced `python-jose[cryptography]` with `PyJWT` in `backend/requirements.txt`
- Updated `backend/core/security.py` to directly use `bcrypt` API for hashing/verification and `PyJWT` for tokens.
- Updated `backend/core/deps.py` to catch `jwt.InvalidTokenError` instead of `jose.JWTError`.
**Remaining:**
- The entire application uses this core auth setup, so no remaining auth pieces for `jose`/`passlib`.
- Evaluate `backend/requirements_win.txt` for same changes if utilized.
**Next session:**
- Look for other deprecated libraries (e.g., aiomysql if modern SQLAlchemy supports better async drivers like asyncmy or asyncpg depending on db).
