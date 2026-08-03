## 2024-08-03 — Migrate from unmaintained passlib and python-jose to standard bcrypt and PyJWT
**Risk identified:** `passlib` is unmaintained and incompatible with modern versions of `bcrypt` (4.0.0+), and `python-jose` is also unmaintained, making them long-term security and compatibility risks.
**Migration target:** Use `bcrypt` directly for password hashing and verification, and `PyJWT` for standard JWT encoding/decoding, which are actively maintained standard libraries in the Python ecosystem.
**Migrated this session:** Replaced `passlib` and `python-jose` with `bcrypt` and `PyJWT` in backend requirements, `backend/core/security.py`, and `backend/core/deps.py`.
**Remaining:** None.
**Next session:** Look for other unmaintained or lagging dependencies to migrate away from.
