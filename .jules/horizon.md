## 2025-07-15 — Migrate away from passlib to native bcrypt
**Risk identified:** The legacy `passlib` library relies on Python's deprecated `crypt` module which breaks in Python 3.13, rendering it completely unmaintained and failing to run on modern runtimes. A future upgrade would block the entire application. Also, passing a password larger than 72 characters crashes the bcrypt algorithm.
**Migration target:** Modern direct dependencies, utilizing `bcrypt` natively.
**Migrated this session:** Migrated `backend/core/security.py` hashing and password validation methods. Removed `passlib` and imported `bcrypt` natively. Brought password limitations to 72 chars in schemas and checks to avoid crashes.
**Remaining:** No further changes needed for `passlib` to `bcrypt` since `bcrypt` natively supports previous hashes properly.
**Next session:** Investigate other potential technical debts in outdated machine learning or cryptography dependencies.
