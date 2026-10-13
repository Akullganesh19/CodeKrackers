## 2025-02-14 — Authentication and JWT Library Modernization
**Risk identified:** `passlib` is abandoned and incompatible with modern bcrypt versions. `python-jose` is unmaintained and considered risky for ongoing use in secure cryptographic operations.
**Migration target:** `bcrypt` directly for password hashing and `PyJWT` for standard JWT handling.
**Migrated this session:** Replaced `passlib` with `bcrypt` in `backend/core/security.py` and `python-jose` with `PyJWT` in `backend/core/security.py` and `backend/core/deps.py`. Updated `backend/requirements.txt` to reflect these changes.
**Remaining:** The migration of backend core auth to modern direct libraries is complete. Need to ensure other microservices or frontend clients are fully compatible (though PyJWT produces standard tokens).
**Next session:** Look into outdated frontend framework practices or review any other lagging backend dependencies (like testing frameworks or legacy async practices).
