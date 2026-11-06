## 2024-05-18 — Collapsed duplicate backend routing layer
**Complexity found:** A duplicate `backend/api/v1/endpoints/` directory containing exact copies of route definitions found in `backend/api/`. `backend/api/v1/api.py` was routing everything through `backend/api/v1/endpoints/`, while `backend/main.py` directly imported from `backend/api/`. This created two sources of truth for routing.
**Why it existed:** Likely an artifact of an incomplete migration or copy-paste architecture that attempted to establish a `/v1` prefix but instead duplicated the entire API logic.
**Eliminated:** `backend/api/v1/` completely removed. All routing logic is now localized purely to `backend/api/`. Modified `backend/api/detection.py` to point to the correct internal endpoint.
**Net change:** Deleted entire directory `backend/api/v1/`. Collapsed two routing concepts into one. Removed unnecessary abstraction layer.
**Next target:** Evaluate frontend state management or API client wrappers for similar redundancy.
