## 2024-10-24 — Redundant v1 API directory eliminated
**Complexity found:** The entire `backend/api/v1/endpoints` directory and `backend/api/v1/api.py`.
**Why it existed:** Historically there might have been a plan for v2, or just following an overly complex boilerplate pattern without a real need, causing all routes to be duplicated or split between `backend/api/` and `backend/api/v1/endpoints/`.
**Eliminated:** The entire `backend/api/v1` directory tree was deleted, moving the single source of truth for routers to `backend/api/`.
**Net change:** Eliminated dozens of duplicate files and a useless abstraction layer.
**Next target:** Any other duplicated abstractions.
