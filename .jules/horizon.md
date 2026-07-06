## 2025-07-05 — Migrate Abandoned Security Dependencies (passlib and python-jose)
**Risk identified:** The backend authentication module relies on `python-jose` for JWT tokens and `passlib` for password hashing. Both libraries are currently unmaintained and abandoned by their communities. `passlib` hasn't had a release since 2020 and has known incompatibilities with modern bcrypt (>=4.0.0). These dependencies represent a compounding security and maintenance risk over the next few years.
**Migration target:** The ecosystem standard `PyJWT` for robust and actively maintained JWT support, and the standard, actively maintained `bcrypt` library directly for password hashing.
**Migrated this session:**
- Updated `backend/requirements.txt` to replace `python-jose[cryptography]` with `PyJWT` and `passlib[bcrypt]` with `bcrypt`.
- Rewrote `backend/core/security.py` to use `bcrypt.checkpw` and `bcrypt.hashpw` directly instead of `CryptContext`.
- Updated PyJWT imports and exception handling (`jwt.InvalidTokenError`) in `backend/core/security.py` and `backend/core/deps.py`.
**Remaining:**
- None for this specific slice.
**Next session:**
- Evaluate other lagging backend dependencies (e.g., aiomysql vs standard async drivers) or minor version lags in major frameworks.