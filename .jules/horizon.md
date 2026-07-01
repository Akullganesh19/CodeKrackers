## 2025-06-28 — Replace passlib with direct bcrypt

**Risk identified:** The backend authentication system relied on the `passlib` library for password hashing. `passlib` is unmaintained and heavily relies on Python's built-in `crypt` module, which is completely removed in Python 3.13. Continuing to use `passlib` poses a major future-proofing risk as it prevents upgrading to newer Python versions.

**Migration target:** The ecosystem standard for password hashing in modern Python applications is directly using the `bcrypt` library or newer alternatives (like `argon2-cffi`), instead of a wrapper like `passlib`.

**Migrated this session:**
- Replaced `passlib.context.CryptContext` with direct `bcrypt` usage in `backend/core/security.py` for both hash generation (`get_password_hash`) and verification (`verify_password`).
- Updated the dependency list in `backend/requirements.txt` to remove `passlib[bcrypt]` and add `bcrypt`.

**Remaining:**
- There are no further password hashing libraries to migrate. This completes the password hashing future-proofing.
- We should monitor other legacy modules like `python-jose` which could also be replaced by maintained alternatives like `PyJWT` in a future session.

**Next session:**
- Evaluate other deprecated/unmaintained dependencies like `python-jose` for JWT handling and plan their migration to standard alternatives.
