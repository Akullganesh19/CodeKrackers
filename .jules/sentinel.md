## 2025-03-08 — Mass Assignment Privilege Escalation in Auth Endpoints
**Attacked:** User registration and OTP verify endpoints (`backend/api/auth.py` & `backend/api/v1/endpoints/auth.py`)
**Found:** The `role` parameter was accepted as optional input in the request body schema with a default of "citizen", and was directly used during User creation, allowing mass assignment to easily escalate privileges to "admin" or "super_admin".
**Severity:** 🔴 Exploitable now
**Fixed or flagged:** Fixed. Removed the `role` field from request schemas entirely, and explicitly hardcoded `role=UserRole("citizen")` (or `role="citizen"`) on the server side during User object creation.
**Systemic pattern:** This mass assignment pattern likely exists in other update/creation endpoints where request models (Pydantic schemas) mirror DB models too closely without separating mutable from immutable fields. Check other user-update endpoints, wallet paths, or permission settings.
