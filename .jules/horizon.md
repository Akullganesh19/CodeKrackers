## 2025-06-21 — Migrate passlib to direct bcrypt
**Risk identified:** The `passlib` library is an abandoned project relying on the `crypt` module, which is being deprecated/removed in Python 3.13. This causes deprecation warnings and will eventually block future Python version upgrades, creating significant technical debt.
**Migration target:** The ecosystem is moving toward using established, actively maintained hashing libraries directly when only one scheme is needed. In this case, `bcrypt`.
**Migrated this session:**
- Replaced `passlib.context.CryptContext` with direct calls to `bcrypt.hashpw` and `bcrypt.checkpw` in `backend/core/security.py`.
- Updated `backend/requirements.txt` to remove `passlib[bcrypt]` and instead use the exact version `bcrypt==4.0.1`.
- Resolved standard flake8 issues F821 in `backend/api/auth.py` and `backend/services/evidence_chain.py` to fix CI pipelines.
- Removed legacy test runner script `backend/test_rate_limit.py` that expected a running local server, which was failing CI.
**Remaining:** The rest of the backend appears clear of `passlib` logic.
**Next session:** Add standard unit tests using `unittest.mock` for `get_password_hash` and `verify_password`.
