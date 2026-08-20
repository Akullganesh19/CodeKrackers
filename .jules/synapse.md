## 2026-05-08 — Auth ↔ Audit (Login Tracking)
**Systems connected:** Auth ↔ Audit
**Intelligence emerged:** We can now track brute-force attacks across IPs, audit user logins for compliance, and correlate user sessions with subsequent actions in the audit log. The audit log is no longer blind to user authentication events.
**Data flows:** Auth sends successful and failed login attempts, lockouts, user identity (email/ID), IP address, and user agent to the Audit system when those events occur in the `/login` and `/verify` endpoints.
**Coupling approach:** Loosely coupled via Event Bridge. Auth emits events (`auth.login_success`, etc.) to a global `event_bus`, and `event_listeners.py` consumes them to write the audit log. Auth passes contextual data without needing to know how Audit stores or processes it.
**Next connection:** Errors ↔ Users. We should consider routing exceptions into user notifications so users know if an error they encountered is a known bug.
