## 2025-08-02 — Migrate from deprecated passlib to standard bcrypt
**Risk identified:** The `passlib` library is unmaintained and causes an `AttributeError` when combined with newer versions of `bcrypt` due to incompatible internal API calls. This creates a risk where future security updates to Python or bcrypt could completely break the authentication module in the backend.
**Migration target:** Switch directly to the modern `bcrypt` module for password hashing and verification instead of relying on `passlib` as a middleman.
**Migrated this session:** Replaced `passlib.context.CryptContext` with native `bcrypt.hashpw` and `bcrypt.checkpw` in `backend/core/security.py`, and updated `backend/requirements.txt`.
**Remaining:** The migration of backend core security is complete, and passlib is fully removed from dependencies. No further passlib dependencies remain.
**Next session:** Look for other older dependencies in `backend/requirements.txt` or `package.json` that might need migration.
