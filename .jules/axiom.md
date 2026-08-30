## 2024-05-18 — Eliminated Unnecessary API Versioning Layer (v1)

**Complexity found:** The backend had an entire duplicate API routing layer (`backend/api/v1/endpoints/`) that shadowed the root `backend/api/` layer. Many files in `backend/api/` were exact duplicates or slightly older versions of what was in `backend/api/v1/endpoints/`. The `backend/main.py` explicitly registered the routes from `backend/api/`, while the unused `backend/api/v1/api.py` registered `backend/api/v1/endpoints/`.

**Why it existed:** It appears to be an artifact of a structural refactor or an aspirational "v1" API design that was never fully adopted, or perhaps an attempt to create versioning that resulted in duplicating all the files and creating confusion.

**Eliminated:**
- The entire `backend/api/v1` directory and all its contents (22 files, over 3,400 lines of code).
- Replaced references to `/api/v1/` with `/api/` in frontend and backend code to point to the actual active endpoints.

**Net change:** -3,412 lines of code, 1 entire abstraction layer/directory structure eliminated.

**Next target:** Identify if `backend/models/orm.py` duplicates the functionality of individual models in `backend/models/*.py`.
