## $(date +%Y-%m-%d) — Deprecated Security Libraries Migration
**Risk identified:** The backend relies on `python-jose` and `passlib`, both of which are deprecated and no longer actively maintained. This poses security and maintenance risks as new vulnerabilities won't be patched.
**Migration target:** The ecosystem has moved toward `PyJWT` for JWT handling and direct use of `bcrypt` for password hashing.
**Migrated this session:** Replaced `python-jose` with `PyJWT` and `passlib` with `bcrypt` in `backend/core/security.py` and `backend/core/deps.py`. Updated `backend/requirements.txt` to reflect these changes.
**Remaining:** No remaining pieces for this specific security dependencies slice.
**Next session:** Look into outdated dependencies in the frontend or other parts of the backend.
