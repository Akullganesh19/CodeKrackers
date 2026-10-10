## 2025-05-23 — Migrate python-jose and passlib to PyJWT and bcrypt
**Risk identified:** `python-jose` and `passlib` are effectively unmaintained or deprecated for modern standards, making them a security risk moving forward.
**Migration target:** `PyJWT` for standard robust JWT validation and `bcrypt` directly for modern hashing support.
**Migrated this session:** Replaced all usages of `python-jose` and `passlib` in `backend/core/security.py` and `backend/core/deps.py`.
**Remaining:** No additional cryptography-related migrations remaining at this time.
**Next session:** Identify next major tech debt block.
