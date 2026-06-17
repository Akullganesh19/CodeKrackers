## 2024-06-17 — [Backend API V1 Layer Eliminated]
**Complexity found:** A completely duplicated API layer inside `backend/api/v1/` (`backend/api/v1/api.py` and `backend/api/v1/endpoints/`).
**Why it existed:** Probably intended as an API versioning strategy, but it resulted in duplicated endpoints from the root `backend/api/` folder.
**Eliminated:** The entire `backend/api/v1` directory was removed because all endpoints have an exact equivalent in the `backend/api/` directory which are already being mounted in `backend/main.py`. The v1 module was completely unused dead code.
**Net change:** -3460 lines deleted, 1 redundant routing abstraction layer removed, 21 duplicate endpoint files deleted.
**Next target:** Finding and collapsing duplicated model imports / resolving `backend.models` versus `backend.models.orm` complexity and schemas.
