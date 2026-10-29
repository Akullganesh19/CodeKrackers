## 2024-10-29 — [Redundant `backend/api/v1` Router and Endpoints Directory]
**Complexity found:** A redundant `backend/api/v1/endpoints/` directory duplicating endpoints already in `backend/api/`. `backend/api/v1/api.py` and `backend/api/v1/endpoints/*` were orphaned when routes were moved to `backend/api/`. The `backend/main.py` explicitly uses `backend/api/*` and does not use `backend/api/v1/api.py` or `backend/api/v1/endpoints/*`.
**Why it existed:** Historical structure for API versioning (v1 vs future v2) which was likely collapsed but left behind orphaned files.
**Eliminated:** The entire `backend/api/v1/` directory.
**Net change:** -22 files, -1000+ lines.
**Next target:** Explore `backend/services` or duplicate frontend API utilities.
