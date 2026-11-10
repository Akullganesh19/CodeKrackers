## 2025-02-28 — python-jose to PyJWT Migration
**Risk identified:** `python-jose` is an unmaintained, deprecated library with stale cryptography dependencies that poses a supply chain and security risk to the authentication system over the coming years.
**Migration target:** `PyJWT`, which is the actively maintained, standard ecosystem choice for JWT generation and validation in Python.
**Migrated this session:** Replaced `python-jose` with `PyJWT` in `backend/core/security.py` and `backend/core/deps.py`, including updating exception handling and dependencies in `requirements.txt` and `requirements_win.txt`.
**Remaining:** None for this specific migration.
**Next session:** Identify the next highest-risk dependency or ecosystem drift.
