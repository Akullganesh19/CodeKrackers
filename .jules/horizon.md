## 2024-05-24 — Migrate python-jose to PyJWT
**Risk identified:** `python-jose` is largely abandoned, meaning it will not receive patches for new security vulnerabilities or updates for newer Python versions. Relying on it for core authentication poses a compounding risk.
**Migration target:** `PyJWT`, which is actively maintained and is the current standard for JWT handling in the Python ecosystem.
**Migrated this session:** Replaced `python-jose[cryptography]` with `PyJWT` in `backend/requirements.txt`. Updated imports and exception handling in `backend/core/security.py` and `backend/core/deps.py`.
**Remaining:** None for this specific library. The authentication stack is fully migrated to PyJWT.
**Next session:** Investigate `passlib` replacement, as it is also seeing decreased maintenance and the ecosystem is moving toward using `bcrypt` directly.
