## 2024-07-16 — Migrate away from deprecated passlib to native bcrypt
**Risk identified:** The backend uses `passlib` for password hashing, which is unmaintained and relies on the deprecated Python `crypt` module (breaking in Python 3.13). This poses a significant future risk of breaking the authentication system upon upgrading the Python version.
**Migration target:** The Python ecosystem is moving towards using the native `bcrypt` package directly for hashing passwords.
**Migrated this session:** Replaced `passlib[bcrypt]` with `bcrypt` in `backend/requirements.txt` and updated `backend/core/security.py` to use `bcrypt.hashpw` and `bcrypt.checkpw`. Also enforced a 72-byte max length limit on passwords to prevent bcrypt crashes.
**Remaining:** The migration of `passlib` for bcrypt is complete in this slice.
**Next session:** Monitor other dependencies like `python-jose` for potential deprecations or migrations.
