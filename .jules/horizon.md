## 2023-10-27 — Migrate from python-jose to PyJWT
**Risk identified:** `python-jose` is an obsolete and no longer actively maintained dependency, making it a high risk for security vulnerabilities over time.
**Migration target:** `PyJWT`, which is the modern, actively maintained standard in the Python ecosystem for JWT generation and validation.
**Migrated this session:** Replaced `python-jose` with `PyJWT` in requirements files (`backend/requirements.txt`, `backend/requirements_win.txt`, `api/requirements.txt`), and updated JWT exception handling (`JWTError` to `jwt.InvalidTokenError`) and imports in `backend/core/deps.py` and `backend/core/security.py`.
**Remaining:** None.
**Next session:** N/A.
