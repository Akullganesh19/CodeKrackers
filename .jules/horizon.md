## 2024-07-02 — Migrate abandoned passlib to direct bcrypt
**Risk identified:** `passlib` is an abandoned library that breaks with modern versions of `bcrypt` due to strict length limitations (throws `ValueError: password cannot be longer than 72 bytes` instead of handling it, and internal version checks are broken). The ecosystem is moving away from the complex legacy `passlib` framework toward using the standard `bcrypt` library directly.
**Migration target:** Use `bcrypt.gensalt()` and `bcrypt.hashpw()` directly instead of `passlib.context.CryptContext`.
**Migrated this session:** Fully migrated `backend/core/security.py` to use `bcrypt` directly, removing `passlib` from dependencies in `backend/requirements.txt` and `api/requirements.txt`.
**Remaining:** No remaining passlib migrations needed. Complete!
**Next session:** Look for other outdated dependencies or ecosystem migrations (such as replacing `aiomysql` if moving to pure postgres, or updating FastAPI versions).
