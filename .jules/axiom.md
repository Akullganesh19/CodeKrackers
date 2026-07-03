## 2025-03-05 — Removed Redundant API Abstraction Layer (backend/api/v1/) and unused Honeypot decoys

**Complexity found:** The entire API structure had duplicated logic inside `backend/api/` and `backend/api/v1/endpoints/`. All files existed in both places, duplicating logic. Furthermore, decoy honeypot endpoints (`honeypot_root.py` and `honeypot_traps.py`) and their models added unnecessary bloat when actual honeypot logic was well-handled in `backend/api/honeypot.py`.
**Why it existed:** Presumably designed to support API versioning (v1), but it was unused and just created a bloated, confusing structure. Decoy honeypots were likely legacy "features" trying to trap bots.
**Eliminated:** Deleted the entire `backend/api/v1/` directory. Removed the redundant import mapping `backend.api.v1.endpoints.threats` in `detection.py`. Deleted `backend/api/honeypot_root.py`, `backend/api/honeypot_traps.py`, and `backend/models/honeypot.py`. Replaced all `api/v1` route occurrences in TS/JS files to `api/`.
**Net change:** Removed over 15 redundant Python files (~1500+ lines). Eliminated API route duplications.
**Next target:** Continue investigating unused or redundant utility files, complex React components that can be flattened, and evaluate the proxy/middleware setup for potential simplification.
