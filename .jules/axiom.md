## 2025-06-25 — Legacy `v1` API Endpoint Layer
**Complexity found:** An entire redundant layer of endpoints existed under `backend/api/v1/endpoints/` alongside the identical primary routes in `backend/api/`. These duplicated endpoints added over 3,000 lines of dead code that engineers had to understand and navigate.
**Why it existed:** Historical API versioning convention where routes were nested under `/api/v1/endpoints/` and managed by a centralized API router `backend/api/v1/api.py`.
**Eliminated:** The entire `backend/api/v1` tree and internal `/api/v1/` string references were removed.
**Net change:** -3,600 lines deleted, 1 redundant abstraction layer (v1 module/router hierarchy) eliminated.
**Next target:** Evaluate redundant API validation logic and middleware chains that parse headers or payloads doing work that could be offloaded entirely to Pydantic definitions.