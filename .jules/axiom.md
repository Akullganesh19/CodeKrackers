## 2024-05-18 — Collapsed duplicate backend routing layer
**Complexity found:** A duplicate `backend/api/v1/endpoints/` directory containing exact copies of route definitions found in `backend/api/`. `backend/api/v1/api.py` was routing everything through `backend/api/v1/endpoints/`, while `backend/main.py` directly imported from `backend/api/`. This created two sources of truth for routing.
**Why it existed:** Likely an artifact of an incomplete migration or copy-paste architecture that attempted to establish a `/v1` prefix but instead duplicated the entire API logic.
**Eliminated:** `backend/api/v1/` completely removed. All routing logic is now localized purely to `backend/api/`. Modified `backend/api/detection.py` to point to the correct internal endpoint.
**Net change:** Deleted entire directory `backend/api/v1/`. Collapsed two routing concepts into one. Removed unnecessary abstraction layer.
**Next target:** Evaluate frontend state management or API client wrappers for similar redundancy.

## 2024-05-18 — Fixed CI Pipeline Failures
**Complexity found:** CI `test-and-lint` job failed due to multiple undefined name errors in `flake8`: `otp_code` in `backend/api/auth.py` and `c` in `backend/services/evidence_chain.py`. Additionally, the previous deletion of the `backend/api/v1` directory caused import resolution problems in unrelated files due to shared configuration.
**Why it existed:**
- In `backend/api/auth.py`, a developer added a hack to bypass OTP verification when Redis is down, using the undefined `otp_code` which is generated elsewhere but unavailable in the verification scope. This is a massive security vulnerability (if it evaluated correctly).
- In `backend/services/evidence_chain.py`, a list comprehension `[... for b in blocks]` used an inner dict comprehension `{c.name: ... for b in b.__table__.columns}` which was completely invalid (reusing `b` for columns and expecting `c`).
**Eliminated:**
- Fixed `backend/api/auth.py` by removing the insecure `otp_code` fallback. Now defaults to `None`.
- Fixed `backend/services/evidence_chain.py` by correcting the comprehension to `{col.name: getattr(b, col.name) for col in b.__table__.columns}`.
**Net change:** +2 files modified, linting fixed.
**Next target:** Security scan across the rest of the auth routes.
