## 2024-05-08 — Account Lockout to Threat Intel Bridge

**Systems connected:** Auth ↔ Threat Intelligence (Analytics/Threats)
**Intelligence emerged:** When a user account gets locked due to multiple failed login attempts in the Auth system, it is automatically surfaced as a HIGH severity Threat in the Threat Intelligence engine for admins to review. This connects brute-force/credential-stuffing attacks to the global threat dashboard.
**Data flows:** Auth System (failed logins/account lockout) -> EventBus -> Threat System (new Threat record)
**Coupling approach:** An isolated `EventBus` module allows `backend/api/auth.py` to publish `account_locked` events anonymously without importing `Threat` models or database sessions directly. The `backend/core/events/listeners.py` handles the subscription, catching the event and recording the Threat, with explicit `try/except` to ensure Auth doesn't fail if DB insert fails.
**Next connection:** Errors ↔ Notifications (routing critical exceptions to Slack/Email for ops).
