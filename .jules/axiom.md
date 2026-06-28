## 2025-06-25 — Elimination of v1 duplicate API endpoints and unused honeypot roots

**Complexity found:** The entire `backend/api/v1/endpoints/` directory was a duplicate of `backend/api/` and `backend/api/honeypot_root.py` and `backend/api/honeypot_traps.py` contained fake endpoints built solely as honeypots with no connection to application logic, polluting the main app routing. Also, `backend/models/honeypot.py` was used only by these traps.
**Why it existed:** A failed migration from a `/v1/` prefix structure to a flat API structure, leaving the old code untouched, and a naive approach to security through obscure honeypot paths.
**Eliminated:** `backend/api/v1/` directory entirely, `backend/api/honeypot_root.py`, `backend/api/honeypot_traps.py`, and `backend/models/honeypot.py`.
**Net change:** -~2000 lines, 1 duplicate abstraction layer removed.
**Next target:** Explore `backend/services/` for duplicate implementations.
