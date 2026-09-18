## 2025-05-08 — [Auth Privilege Escalation]
**Attacked:** User registration and OTP verification endpoints
**Found:** The endpoints trust user-supplied roles, allowing any user to register as an admin or super_admin.
**Severity:** 🔴
**Fixed or flagged:** Fixed by forcing the default role to `UserRole.CITIZEN` or `"citizen"` on user creation.
**Systemic pattern:** Blindly trusting client input for sensitive fields like roles. Check for other similar vulnerabilities.
