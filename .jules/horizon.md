## 2025-06-23 — Passlib to Bcrypt Migration
**Risk identified:** The backend authentication relied on `passlib` for password hashing. `passlib` is effectively abandoned and triggers deprecation warnings in Python 3.11+, specifically because its dependency on the standard library `crypt` module breaks in Python 3.13 where `crypt` is completely removed. This creates a hard blocker for future Python upgrades.
**Migration target:** Direct use of the actively maintained `bcrypt` library, matching modern security standards without legacy abstraction layers.
**Migrated this session:** Replaced `passlib` with `bcrypt==4.0.1` in `backend/core/security.py`. Removed `passlib` from all requirement files. Fixed undefined variable errors in related module verification (`auth.py` and `evidence_chain.py`).
**Remaining:** 100% of the hashing migration is complete.
**Next session:** Look for other deprecated libraries like `python-jose` which could be moved to standard `PyJWT` or similar maintained modern libraries.
