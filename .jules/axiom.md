## 2024-11-02 — Redundant API endpoints structure
**Complexity found:** The codebase contained two versions of the API endpoints, with `backend/api/v1/endpoints/` largely mirroring `backend/api/`. `backend/main.py` directly includes endpoints from `backend/api/`, not `backend/api/v1/`.
**Why it existed:** Likely an artifact of an incomplete refactoring or migration where a `/v1` structure was introduced or retired without completing the cleanup.
**Eliminated:** The entire `backend/api/v1` directory has been removed, eliminating a large chunk of duplicated routing complexity.
**Net change:** Removed `backend/api/v1` (approximately 21 files).
**Next target:** Any other duplicated API logic or unnecessary abstraction layers.
