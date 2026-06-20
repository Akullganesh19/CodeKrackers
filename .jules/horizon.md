## 2026-06-20 — Pydantic V2 Config Migration
**Risk identified:** Backend Pydantic models rely on V1-style `class Config`, triggering V2 deprecation warnings (`ConfigDict` needed). This pattern will break entirely in future updates and adds confusion for developers assuming V2 standards.
**Migration target:** Migrate to Pydantic V2 standard configuration patterns. Use `model_config = ConfigDict(...)` for standard models and `model_config = SettingsConfigDict(...)` for `pydantic-settings` BaseSettings models.
**Migrated this session:**
- `backend/core/config.py`: Migrated `Settings` to use `SettingsConfigDict`.
- `backend/models/user.py`: Migrated `UserBase` to use `ConfigDict`.
- `backend/models/threat.py`: Migrated `ThreatBase` to use `ConfigDict`.
**Remaining:** Any remaining Pydantic models across the codebase that might still be using `class Config` need to be checked and migrated.
**Next session:** Grep the codebase for `class Config` in `pydantic` context to catch any stragglers, and handle V2-specific validation/serialization differences if necessary.
