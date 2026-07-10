## 2026-07-10 — Auth Failure to Threat Intel Log

**Systems connected:** Auth System ↔ Audit Logging System
**Intelligence emerged:** When a user account exceeds `MAX_LOGIN_ATTEMPTS` and becomes locked, this critical piece of information is now shared with the Audit Logging system. Security teams and threat intelligences now receive this information as a potential sign of a brute-force attack or credential stuffing attempt.
**Data flows:** Auth System (api/auth.py) → EventBus → Listeners (core/events/listeners.py) → Audit Log System (models/audit.py, services/audit.py). Auth system passes user_id, email, and IP address.
**Coupling approach:** The two systems are decoupled through an EventBus implementation. The auth system simply publishes an `ACCOUNT_LOCKED` event without directly depending on the Audit Logger, and a lightweight listener binds to that event asynchronously. Removing the Audit Logger or EventBus listeners will not break the core authentication flow.
**Next connection:** Correlate FIR (First Information Reports) creation with anomaly detectors to highlight system-wide spikes in specific fraud trends.
