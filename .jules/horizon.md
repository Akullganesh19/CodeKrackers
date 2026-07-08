## 2024-05-24 — Security Library Migration
**Risk identified:** The backend uses `python-jose` and `passlib`, which are deprecated, abandoned, and have accumulating security risks and compatibility issues (especially `passlib` failing on `bcrypt` >= 4.0.0). These represent a high risk of breaking changes in future Python upgrades.
**Migration target:** The modern, standard, and actively maintained ecosystem libraries: `PyJWT` for token encoding/decoding and `bcrypt` directly for password hashing.
**Migrated this session:**
- Replaced `python-jose[cryptography]` with `PyJWT` and `passlib[bcrypt]` with `bcrypt` in `backend/requirements.txt`.
- Refactored `backend/core/security.py` to use `bcrypt` functions directly (`hashpw` and `checkpw`) and standard `jwt`.
- Updated `backend/core/deps.py` to catch `jwt.InvalidTokenError` instead of `jose.JWTError`.
**Remaining:** The migration of security libraries for JWT and password hashing is complete. No further work is needed on this specific slice.
**Next session:** Look for other legacy dependencies or structural patterns (such as outdated async drivers) that represent the next highest risk.
