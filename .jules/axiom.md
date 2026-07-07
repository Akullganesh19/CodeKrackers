## 2024-05-18 — Removed Redundant API v1 Routing Layer
**Complexity found:** The entire `backend/api/v1/endpoints/` directory was practically a mirror of the `backend/api/` directory with duplicated router code and an extra `api.py` orchestrating them unnecessarily, even though `backend/main.py` was directly including the routers from `backend/api/` instead of `backend/api/v1`.
**Why it existed:** It appeared to be a relic of an attempted (or abandoned) API versioning strategy, or an older iteration of the routing structure that was never fully cleaned up.
**Eliminated:** The `backend/api/v1` directory and its contents were completely removed.
**Net change:** 20 files deleted, removing hundreds of lines of duplicate routing code.
**Next target:** Continue looking for duplication between the top-level API implementation and inner routers.
