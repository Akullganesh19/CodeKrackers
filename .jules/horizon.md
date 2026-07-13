## 2025-07-13 — Replace passlib and python-jose with modern alternatives
**Risk identified:** The backend uses `passlib` for password hashing and `python-jose` for JWT tokens. Both of these libraries are unmaintained/abandoned and missing crucial updates for modern Python versions and security patches.
**Migration target:** Switch to `bcrypt` (native, actively maintained) for password hashing and `PyJWT` (actively maintained, modern standard) for JWT handling.
**Migrated this session:** Replaced `passlib` with `bcrypt` in `backend/core/security.py` and modified password policy limit to 72 chars to match bcrypt's requirements. Replaced `python-jose` with `PyJWT` in `backend/core/security.py` and `backend/core/deps.py`. Updated `requirements.txt` in both `backend/` and `api/` directories.
**Remaining:** Verify if any other peripheral scripts or microservices use passlib or python-jose and remove them completely from the environment.
**Next session:** Complete verification of other microservices, and review if any other security-related deprecations exist (like older hashing algorithms).
