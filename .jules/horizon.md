## 2025-02-23 — Migrate away from passlib and Pydantic V1 configs
**Risk identified:** `passlib` relies on the built-in `crypt` module which was removed in Python 3.13, causing deprecation warnings and future broken builds. Also, Pydantic V1 `class Config` usage throughout the models caused loud deprecation warnings because the project is already using Pydantic V2 (`pydantic-settings`). Leaving these deprecated patterns clutters logs, obscures real bugs, and increases the difficulty of future migrations.
**Migration target:** Direct use of `bcrypt` for password hashing and verification. Use of `model_config = ConfigDict(...)` for Pydantic V2 models.
**Migrated this session:**
- `backend/core/security.py` now uses `bcrypt` directly.
- Removed `passlib` from `backend/requirements.txt` and pinned `bcrypt==4.0.1` (due to known issues with 5.x on this environment).
- Updated `backend/core/config.py`, `backend/models/user.py`, and `backend/models/threat.py` to use Pydantic V2 `model_config` patterns.
**Remaining:** The rest of the codebase needs to be audited to ensure no other straggling `class Config` definitions exist (though grep indicates the main ones are done). Some older schema files under `backend/schemas/` were found in memory but might not be in the current source tree, so these should be double checked in future sessions.
**Next session:** Ensure that no other deprecated Pydantic features (e.g., `.dict()` instead of `.model_dump()`) are used elsewhere in the codebase.
