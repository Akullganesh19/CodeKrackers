## 2024-05-18 — JWT Library Migration
**Risk identified:** The backend uses `python-jose` for JWT handling. `python-jose` is effectively abandoned (no meaningful updates in years, 500+ open issues, fails with newer cryptography libraries, unmaintained). It will become a massive security and maintenance risk over the next 1-2 years.
**Migration target:** `PyJWT`, which is the actively maintained, modern standard for JWT handling in Python, natively supports modern cryptography, and has a very similar API.
**Migrated this session:** Replaced `python-jose` with `PyJWT` in `requirements.txt`, `backend/core/security.py`, and `backend/core/deps.py`.
**Remaining:** None for this specific slice.
**Next session:** Start migrating synchronous, blocking I/O calls to async/await or investigate SQLAlchemy V2 2.0 style queries.
