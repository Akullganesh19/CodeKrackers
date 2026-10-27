## 2024-05-17 — Collapsed backend/api/v1 router layer
**Complexity found:** The `backend/api/` directory contained original router implementations (e.g. `backend/api/threats.py`), but an entire redundant routing layer existed in `backend/api/v1/endpoints/` (e.g. `backend/api/v1/endpoints/threats.py`), which just re-implemented or wrappered the exact same endpoints.
**Why it existed:** Likely an artifact of an incomplete "v1" refactor or an over-engineered versioning system where the versioning was never actually utilized for differing logic, resulting in 20+ duplicated files.
**Eliminated:** The entire `backend/api/v1/` directory. All imports have been updated to point directly to `backend/api/`. `backend/api/v1/api.py` was also removed as it was redundant. `backend/main.py` already loaded the base routes directly, bypassing `api_router`.
**Net change:** Eliminated 21 files, removing an entire unnecessary abstraction layer (the `v1/endpoints` directory).
**Next target:** Identify if `backend/models` and `backend/schemas` contain redundant structural overlap (e.g. identical Pydantic and SQLAlchemy representations that could be collapsed using SQLModel).
