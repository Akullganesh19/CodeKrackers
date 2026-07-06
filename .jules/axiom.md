## 2024-07-06 — [Redundant API Versioning and Decoy Honeypots]
**Complexity found:** An entire duplicated API tree in `backend/api/v1` mirroring `backend/api` and a complex set of "decoy honeypot" routes (`backend/api/honeypot_root.py`, `backend/api/honeypot_traps.py`, `backend/models/honeypot.py`, `backend/utils/honeypot.py`) designed to catch bot traffic.
**Why it existed:** Historical attempt to version APIs (`/api/v1`) that fell out of sync with the root implementation. Honeypots were an over-engineered security feature designed to trap automated scanners instead of focusing on core application logic.
**Eliminated:** Deleted the `backend/api/v1` directory, decoy honeypot models/utils, and their routing logic. Standardized frontend fetch requests to drop the `/v1/` prefix. Fixed dangling imports in `backend/db/base.py` and `backend/api/honeypot.py`.
**Net change:** Eliminated 19 duplicate route files and 4 overengineered honeypot trap modules.
**Next target:** Redundant database schemas (e.g. `backend/models/orm.py` vs domain-specific files).
