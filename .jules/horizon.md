## 2025-02-14 — Migrate deprecated security dependencies (python-jose & passlib) to modern standards
**Risk identified:** The codebase relies on `python-jose` for JWT handling and `passlib` for password hashing. Both libraries are currently unmaintained/abandoned in the Python ecosystem. `python-jose` has unresolved security issues and compatibility issues with newer versions of cryptography, while `passlib` is deprecated and incompatible with modern `bcrypt` (>=4.0.0). This technical debt compounds as newer Python environments and security requirements evolve.
**Migration target:** Replace `python-jose` with the standard and actively maintained `PyJWT` library. Replace `passlib` with direct usage of the modern `bcrypt` library (which is already installed as a dependency for passlib and is the de facto standard).
**Migrated this session:**
- Updated `backend/requirements.txt` and `api/requirements.txt` to remove `python-jose` and `passlib`, and replaced them with `PyJWT` and `bcrypt`.
- Refactored `backend/core/security.py` to use `jwt` from `PyJWT` and direct `bcrypt` for password hashing.
- Refactored `backend/core/deps.py` to import `InvalidTokenError` from `jwt` instead of `JWTError` from `jose`.
**Remaining:** None for this specific dependency migration.
**Next session:** Look into potential async database testing patterns or any framework version lags (e.g., FastAPI or SQLAlchemy).
