## 2026-07-28 — [Duplicate v1 API Endpoints]
**Complexity found:** An entire `/api/v1` layer mirroring the functionality and routing of the standard `/api` endpoints, resulting in nearly identical code files and routing logic in both `backend/api/` and `backend/api/v1/endpoints/`.
**Why it existed:** Most likely a historical relic from a planned or partially completed versioning strategy where standard endpoints were duplicated.
**Eliminated:** The entire `backend/api/v1/` directory and all duplicated routes. `backend/api/v1/api.py` and `backend/api/v1/__init__.py` were deleted. NextJS API fetches and internal test scripts were updated to use standard `/api` routes.
**Net change:** +25 lines added, -3491 lines removed, 1 major abstraction layer eliminated.
**Next target:** Explore `backend/core/` and `backend/services/` for duplicated data transformation pipelines or unneeded wrapper classes.
