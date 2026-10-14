## 2024-10-14 — Cryptography Modernization
**Risk identified:** The backend authentication system relies on `passlib` (which is abandoned, unmaintained, and incompatible with modern bcrypt versions) and `python-jose` (which is unmaintained and considered deprecated by the community). These represent a significant security and compatibility risk over the next few years.
**Migration target:** The Python ecosystem has settled on using the `bcrypt` library directly for password hashing and `PyJWT` for JWT signing and validation.
**Migrated this session:** Swapped out `passlib` for direct `bcrypt` hashing/verification, and replaced `python-jose` with `PyJWT` in `requirements.txt`, `backend/core/security.py`, and `backend/core/deps.py`.
**Remaining:** This completes the migration for core security dependencies.
**Next session:** Look into outdated AI models or frontend dependencies.
