## 2024-05-18 — Auth Ecosystem Modernization (passlib/jose to bcrypt/PyJWT)
**Risk identified:** The codebase relies on `python-jose` and `passlib`, both of which are essentially abandoned by their maintainers. In particular, `passlib` has poor compatibility with modern Python and native `bcrypt` versions (often breaking on modern bcrypt ≥ 4.0.0 due to removed functions). This will eventually cause unexpected install and runtime breakages, posing a significant security and stability risk.
**Migration target:** Modern, actively maintained security primitives. Specifically, `PyJWT` for JWT signing and verification, and raw `bcrypt` for password hashing and validation.
**Migrated this session:**
- Removed `python-jose` and `passlib` from `backend/requirements.txt` and replaced them with `PyJWT` and `bcrypt`.
- Migrated `backend/core/security.py` to use `jwt` (PyJWT) and `bcrypt` directly. Rewrote the password hashing and verification functions to encode string values appropriately and gracefully handle hashing errors.
- Migrated `backend/core/deps.py` to import and handle `PyJWTError` instead of `jose`'s `JWTError`.
**Remaining:**
- Full audit of any downstream clients or internal microservices that may validate tokens (though PyJWT's standard JWT formats should maintain full compatibility with valid old tokens).
- Removal of any other abandoned security libraries if discovered.
**Next session:**
- Look into updating any Pydantic V1 usages to V2 (if present).
- Investigate other backend dependencies that may be out of date (e.g., aiomysql -> asyncpg if migrating away from MySQL, etc).
