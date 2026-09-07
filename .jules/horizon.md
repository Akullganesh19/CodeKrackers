## 2025-01-20 — Deprecated Security Libraries (passlib and python-jose)

**Risk identified:** The backend uses `passlib` and `python-jose` for password hashing and JWT encoding. Both libraries are unmaintained (last releases in 2020). Critically, `passlib` relies on the standard library `crypt` module which is officially removed in Python 3.13, meaning the application will fatally crash upon upgrading Python versions. `python-jose` has unpatched vulnerabilities and lacking modern Python support.
**Migration target:** Modern Python standard is to use `bcrypt` directly for password hashing, and `PyJWT` for JWTs.
**Migrated this session:** Migrated `backend/core/security.py` to use `bcrypt` directly and `PyJWT`. Updated `backend/requirements.txt` to remove `passlib[bcrypt]` and `python-jose[cryptography]`, replacing them with `bcrypt` and `PyJWT`.
**Remaining:** None for this specific library replacement, it's fully migrated.
**Next session:** Look into migrating frontend's `create-react-app` or older `useEffect` data-fetching to a modern server components approach, or check if `reportlab` can be swapped for a more modern async-friendly PDF generator.
