## 2023-10-24 — Redundant v1 API Routing Directory

**Complexity found:** A completely duplicated backend API routing layer. The repository contained `backend/api/` and `backend/api/v1/endpoints/`. Many routers in `backend/api/` were slightly different or just completely replicated with minor variations. The actual application (`backend/main.py`) included routers from `backend/api/`. `backend/api/v1/api.py` was an APIRouter that included the redundant `backend/api/v1/endpoints/` and some frontend/mobile code referenced `/api/v1` routes.

**Why it existed:** Likely an incomplete or abandoned attempt to version the API, or an artifact from generating the project using a template that structured it with `api/v1/endpoints` while another developer structured it flatter.

**Eliminated:** The entire `backend/api/v1` directory tree (21 files, ~3400 lines of redundant code) was removed. References to `/api/v1/` in the codebase were replaced with `/api/` to point directly at the active root-level routers in `backend/api/`.

**Net change:** 21 files deleted, over 3000 lines of code removed. One entire layer of API routing duplication eliminated.

**Next target:** Explore `backend/services/` and `backend/core/` for redundant abstractions.
