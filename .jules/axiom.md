## 2024-05-18 — [Eliminated Duplicate API Layer]
**Complexity found:** `backend/api/v1/endpoints/` and `backend/api/v1/api.py` duplicating `backend/api/` logic entirely. `backend/api/v1/endpoints/` files seem to be older or a completely duplicated version of the endpoints in `backend/api/`. `main.py` ignores `backend/api/v1/api.py` and manually includes routers from `backend/api/`.
**Why it existed:** Probably a failed or half-done refactoring from an old flat layout to a nested `v1` layout or vice-versa, leaving both in the tree but importing some randomly.
**Eliminated:** Entire `backend/api/v1/` directory and corrected references.
**Net change:** [-2000 lines, -20 duplicated files/routers]
**Next target:** Undetermined
