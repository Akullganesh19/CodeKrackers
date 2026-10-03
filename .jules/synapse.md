## YYYY-MM-DD — Connect Auth and Audit
**Systems connected:** Auth ↔ Audit Logging
**Intelligence emerged:** Failed login attempts, lockouts, and successful logins are now logged to the central forensic audit trail, allowing security teams to correlate authentication anomalies with IP addresses and user agents.
**Data flows:** Auth service -> Audit service
**Coupling approach:** The Auth service imports the `log_event` and `AuditAction` from `backend.services.audit` and calls it asynchronously or synchronously where authentication events occur, keeping the implementation thin.
**Next connection:** Errors ↔ Users
