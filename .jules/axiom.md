## 2024-05-24 — Duplicate API v1 Endpoints Directory Removed
**Complexity found:** A complete duplicate of the `backend/api/` routing layer existed in `backend/api/v1/endpoints/`, consisting of 21 files.
**Why it existed:** The `backend/api/v1/` structure likely existed as the original API design, but the entrypoint `backend/main.py` directly mounts the files from `backend/api/`. As a result, the `backend/api/v1/endpoints/` directory became dead code, but was kept up-to-date and even had test/import references leading to confusion.
**Eliminated:** The entire `backend/api/v1/` directory.
**Net change:** -22 files, hundreds of redundant lines of code deleted. 1 abstraction layer (the `v1` API router) eliminated.
**Next target:** Check for redundancy in `backend/services` or data models.
