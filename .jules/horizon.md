## 2024-05-24 — [Passlib to Bcrypt]
**Risk identified:** The `passlib` library is unmaintained and relies on the deprecated `crypt` module, which breaks in Python 3.13. It is a security risk.
**Migration target:** Native `bcrypt` library, which is actively maintained.
**Migrated this session:** `backend/core/security.py` has been updated to use `bcrypt` directly instead of `passlib.context.CryptContext`. The password length limit has been updated to 72 bytes.
**Remaining:** N/A. The single `passlib` use case has been fully migrated.
**Next session:** Look for other deprecated libraries or dependencies.
