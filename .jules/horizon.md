## 2025-02-23 — Migrate Auth Libraries to Modern Standard
**Risk identified:** The backend was using passlib[bcrypt] and python-jose[cryptography]. passlib is abandoned and incompatible with modern bcrypt versions (crashing on bcrypt 4.x), and python-jose is largely unmaintained. Continuing to use them prevents dependency updates and introduces security/maintenance risks over time.
**Migration target:** The modern ecosystem standard: using the bcrypt library directly for password hashing and verification, and PyJWT for JSON Web Tokens.
**Migrated this session:** Replaced passlib with bcrypt and python-jose with PyJWT in requirements.txt, backend/core/security.py, and backend/core/deps.py. Wrote compatibility layers to handle string/bytes encoding and interface differences natively without breaking existing tests.
**Remaining:** No remaining work for this specific auth library migration; it is fully replaced.
**Next session:** Investigate other potential abandoned dependencies in the FastAPI backend or start reviewing the frontend for outdated React/Next.js paradigms.
