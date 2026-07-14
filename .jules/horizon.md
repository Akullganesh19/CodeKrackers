## 2024-05-18 — Migrate python-jose and passlib to PyJWT and bcrypt

**Risk identified:** `python-jose` is unmaintained. `passlib` is abandoned and relies on the `crypt` module which is deprecated and removed in Python 3.13, causing potential crashes during password hashing.
**Migration target:** Native `bcrypt` for password hashing, and `PyJWT` for JWT generation and validation. Both are modern, well-maintained standards.
**Migrated this session:** Fully replaced `passlib` with `bcrypt`, including enforcing the 72-byte max length limit, and fully replaced `python-jose` with `PyJWT` in `backend/core/security.py`, `backend/core/deps.py`, and the `requirements.txt` files.
**Remaining:** None.
**Next session:** Look for further dependency deprecations.
