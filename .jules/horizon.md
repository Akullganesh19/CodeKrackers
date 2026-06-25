## 2025-06-25 — passlib to bcrypt Migration
**Risk identified:** `passlib` is deprecated and causes Python 3.13 deprecation warnings related to the `crypt` module.
**Migration target:** Use `bcrypt` directly to maintain compatibility and eliminate deprecated dependencies.
**Migrated this session:** Replaced `passlib.context.CryptContext` with direct `bcrypt` calls (`bcrypt.hashpw` and `bcrypt.checkpw`) in `backend/core/security.py`. Removed `passlib` dependency from `backend/requirements.txt` and `api/requirements.txt` while enforcing `bcrypt==4.0.1` version.
**Remaining:** No further migration needed for this specific dependency as the relevant hashing functionality is completely migrated.
**Next session:** Look for other deprecated patterns or dependencies.
