## 2024-10-24 — Migrate authentication libraries to modern standards (bcrypt/PyJWT)

**Risk identified:** The backend uses `passlib` for password hashing and `python-jose` for JWT operations. `passlib` is unmaintained and incompatible with modern `bcrypt` versions (4.0.0+), leading to potential installation or runtime failures in newer environments. `python-jose` is also largely unmaintained and has known vulnerabilities. Continuing to use these libraries creates significant security and compatibility risks that will compound as the ecosystem moves forward.

**Migration target:** The ecosystem is moving toward well-maintained, native libraries like `bcrypt` directly (for password hashing) and `PyJWT` (for JWT encoding/decoding). These libraries are actively supported and compatible with modern Python environments.

**Migrated this session:**
- Replaced `passlib` with `bcrypt` in `backend/core/security.py`.
- Replaced `python-jose` with `PyJWT` in `backend/core/security.py` and `backend/core/deps.py`.
- Updated `backend/requirements.txt` to reflect the new dependencies (`bcrypt`, `PyJWT`).

**Remaining:** None for this specific migration. All usages of `passlib` and `python-jose` in the backend have been replaced.

**Next session:** Look for other outdated or deprecated dependencies in the backend or frontend (e.g., checking `package.json` for major version lags).
