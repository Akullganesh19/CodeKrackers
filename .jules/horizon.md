## 2024-11-04 — Migrate legacy auth libraries
**Risk identified:** The legacy auth libraries python-jose and passlib are largely unmaintained. Continuing to use them is a risk.
**Migration target:** Modern standard libraries PyJWT and bcrypt.
**Migrated this session:** Entirely replaced passlib and python-jose with bcrypt and PyJWT in backend/core/security.py and backend/core/deps.py.
**Remaining:** None for this migration.
**Next session:** None.
