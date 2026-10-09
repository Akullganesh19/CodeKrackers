## 2025-02-15 — Migrate passlib and python-jose to bcrypt and pyjwt
**Risk identified:** `passlib` is abandoned and incompatible with modern bcrypt versions, and `python-jose` is unmaintained and relies on older cryptography standards. This risks security vulnerabilities, compatibility issues, and broken builds in the future.
**Migration target:** Move to native `bcrypt` for password hashing and `PyJWT` for JWT signing and validation, which are actively maintained and standard for the ecosystem.
**Migrated this session:** Replaced `passlib` with `bcrypt` and `python-jose` with `PyJWT` in `backend/core/security.py` and `backend/core/deps.py`. Updated `backend/requirements.txt` and `api/requirements.txt`.
**Remaining:** No remaining tasks for this specific migration in the core backend. Other potential unmaintained libraries may exist but this risk is cleared.
**Next session:** Investigate other potential legacy or risky dependencies, such as standardizing FastAPI dependencies or checking for other deprecated Pydantic models/constructs if any.
