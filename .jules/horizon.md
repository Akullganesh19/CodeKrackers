## 2025-07-11 — [Migrate from abandoned passlib/jose to bcrypt/PyJWT]
**Risk identified:** The backend authentication system relied on `python-jose` for JWT validation and `passlib` for password hashing. Both packages are essentially abandoned (passlib is broken in modern python with bcrypt >=4.0.0, and jose is unmaintained). This created a severe and compounding security/compatibility risk.
**Migration target:** The ecosystem standard natively uses `PyJWT` for robust token handling and the canonical `bcrypt` library for hashing without passlib wrappers.
**Migrated this session:**
- Updated `backend/requirements.txt` to remove `passlib` and `python-jose`, adding `bcrypt` and `PyJWT`.
- Refactored `backend/core/security.py` to use `bcrypt` directly, safely enforcing 72-byte maximum length constraints on passwords.
- Refactored `backend/core/deps.py` to handle exceptions via `InvalidTokenError` instead of `JWTError`.
- Created integration unit tests in `backend/tests/test_security.py` to ensure backwards compatibility for verification of password hashes and JWT decodes.
**Remaining:** No remaining pieces for this specific auth migration, though other legacy dependencies (like testing packages) might need review in future.
**Next session:** Evaluate Python framework or frontend dependency lag (e.g. Next.js 16 to ecosystem standard Next 15 stable/App Router standards).
