## 2024-06-18 — Auth Library Migration
**Risk identified:** The backend depends on `passlib` and `python-jose`, which are deprecated, unmaintained, or generally being moved away from in the Python ecosystem. Deferring this migration increases the risk of unpatched security vulnerabilities and incompatibility with newer Python versions.
**Migration target:** The ecosystem standard is migrating to `bcrypt` directly for password hashing and `PyJWT` for JWT token handling.
**Migrated this session:**
- Updated `backend/requirements.txt` to remove `passlib[bcrypt]` and `python-jose[cryptography]`, replacing them with `bcrypt` and `PyJWT`.
- Migrated `backend/core/security.py` to use `bcrypt` and `jwt` directly.
- Migrated `backend/core/deps.py` to use `jwt.exceptions.InvalidTokenError` instead of `jose.JWTError`.
**Remaining:** The migration of the core authentication primitives in `security.py` is complete. We need to verify if any other files are importing `passlib` or `jose` and update them if necessary, but initial grep suggests these are the main ones.
**Next session:** Check if there are other areas of the backend or external scripts relying on the old auth libraries, run full test suite to ensure the new auth mechanisms work seamlessly.
