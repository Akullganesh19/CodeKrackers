## 2024-06-29 — Passlib to Bcrypt Migration
**Risk identified:** The project uses `passlib[bcrypt]` for password hashing. However, `passlib` relies on Python's `crypt` module which is deprecated in Python 3.11 and removed in Python 3.13, causing compatibility issues with modern Python versions and latest bcrypt libraries.
**Migration target:** The ecosystem is moving away from `passlib` towards direct `bcrypt` usage for password hashing.
**Migrated this session:** Replaced `passlib.context.CryptContext` with pure `bcrypt` in `backend/core/security.py` for both generating and verifying hashes. Updated `backend/requirements.txt` and `api/requirements.txt` dependencies.
**Remaining:** None for this specific component.
**Next session:** Look for other outdated dependencies or legacy Python module usages.
