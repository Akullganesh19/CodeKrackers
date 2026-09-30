## 2024-10-27 — [Duplicate API v1 Routing Layer]
**Complexity found:** An entire duplicate routing layer `backend/api/v1/endpoints/` existed alongside `backend/api/`.
**Why it existed:** Likely leftover from a botched refactoring or an abandoned attempt to introduce API versioning, leading to 20+ duplicated files.
**Eliminated:** Deleted `backend/api/v1/` entirely, redirecting all remaining stray frontend/test paths directly to `/api/`.
**Net change:** -20+ files, thousands of lines of duplicated routing logic eliminated.
**Next target:** Explore `backend/services/` for duplicated background jobs or overlapping anomaly detection pipelines.
