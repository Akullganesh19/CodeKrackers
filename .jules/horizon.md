## 2024-05-15 — Replace unmaintained security dependencies

**Risk identified:**
- `passlib` hasn't been updated since 2020 (v1.7.4) and breaks with modern versions of `bcrypt` (v4+) because `bcrypt` removed `__about__` which `passlib` expects.
- `python-jose` hasn't had a release in over 2 years and is largely abandoned by maintainers. `PyJWT` is the active standard now.

**Migration target:**
- Use `bcrypt` directly for password hashing. It's the standard and actively maintained.
- Use `PyJWT` for JWT signing and validation.

**Migrated this session:**
- Swapped `passlib` with `bcrypt` in `backend/core/security.py`
- Swapped `python-jose` with `PyJWT` in `backend/core/security.py` and `backend/core/deps.py`
- Updated `backend/requirements.txt` and `api/requirements.txt` to remove old deps and add `bcrypt` and `PyJWT`

**Remaining:**
- Verify we have no other references to passlib or python-jose (grep codebase).
- Monitor other deprecated dependencies in the future.

**Next session:**
- Ensure all tests pass.
