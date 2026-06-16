## 2025-06-16 — Authentication & Crypto Primitives Migration
**Risk identified:** The backend uses `passlib` (unmaintained, breaks with `bcrypt` >= 4.0.0 due to removed `__about__` attribute) and `python-jose` (abandoned library) for password hashing and JWT encoding/decoding. These are high-risk legacy decisions; as security libraries age, lack of updates poses severe vulnerability risks, making the tech debt compound over time.
**Migration target:** The Python ecosystem has coalesced around `bcrypt` directly for hashing and `PyJWT` for JWT operations.
**Migrated this session:** Replaced `passlib` with direct `bcrypt` calls and replaced `python-jose` with `PyJWT` in `backend/core/security.py`, `backend/core/deps.py`, and the `requirements.txt` files. Verified behaviour compatibility for hashing and token decode.
**Remaining:**
1. The frontend still uses `jose` in `package.json` for some reason (maybe edge runtime). It might be worth replacing `jose` with `jose` equivalents or natively using Web Crypto API.
2. Ensure database user migrations (if any exist) handle the `bcrypt` format identically (they should, since passlib used bcrypt under the hood).
**Next session:** Investigate the frontend usage of `jose` in Next.js and migrate to a more modern approach or verify if it's currently necessary for Next.js edge-compatible auth.
