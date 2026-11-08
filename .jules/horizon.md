## 2025-02-14 — JWT Library Migration
**Risk identified:** The `python-jose` library is unmaintained and deprecated, posing future security and compatibility risks.
**Migration target:** The `PyJWT` library, which is actively maintained and serves as the ecosystem standard for JWT handling in Python.
**Migrated this session:** Replaced `python-jose` with `PyJWT` in `requirements.txt` and updated the `jwt` imports and exception handling in `backend/core/security.py` and `backend/core/deps.py`.
**Remaining:** None for this specific migration.
**Next session:** Look for other legacy cryptography packages (like `passlib` settings) that might need modernizing.
