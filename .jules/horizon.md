## 2023-10-27 — passlib to bcrypt migration
**Risk identified:** `passlib` is deprecated and effectively abandonware. It relies on the `crypt` module which is removed in Python 3.13, causing deprecation warnings and potential breakages.
**Migration target:** Direct use of the `bcrypt` library for password hashing and verification.
**Migrated this session:** Replaced `passlib` with `bcrypt` in `backend/core/security.py`, updated dependencies in `backend/requirements.txt` and `api/requirements.txt`.
**Remaining:** None.
**Next session:** Complete.
