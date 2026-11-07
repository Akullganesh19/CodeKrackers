## 2024-05-19 — Remove passlib and python-jose

**Risk identified:** `passlib` is largely unmaintained and has known compatibility issues with newer versions of `bcrypt`. `python-jose` is also seeing decreased maintenance compared to `PyJWT`.
**Migration target:** Migrate to using `bcrypt` directly for password hashing and `PyJWT` for JWT generation/validation.
**Migrated this session:** Replaced `passlib` with `bcrypt` in `backend/core/security.py`. Replaced `python-jose` with `PyJWT` in `backend/core/security.py` and `backend/core/deps.py`. Updated `requirements.txt` and `requirements_win.txt`.
**Remaining:** None for this specific authentication migration.
**Next session:** Assess other potential migrations, possibly focusing on framework or ORM modernization.
