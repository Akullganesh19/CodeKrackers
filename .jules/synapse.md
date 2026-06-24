## 2025-06-25 — [Account Takeover Intelligence Bridge]
**Systems connected:** Auth ↔ Analytics/Threats
**Intelligence emerged:** Proactive detection and logging of brute force and account takeover attempts within the threat management dashboard. Previously, these were just rejected logins in the auth system.
**Data flows:** When an account hits the max failed login attempt threshold and is locked by the `Auth` system, an event (`user.locked`) is dispatched. The `Analytics/Threats` listener receives this and generates a high-severity `Threat` record attributed to the user and the attacking IP.
**Coupling approach:** Event Bus (`EventBus`). The Auth system blindly publishes the event without knowing who listens, maintaining strict loose coupling. The intelligence logic lives entirely within `core/events/listeners.py`.
**Next connection:** Errors ↔ Users (surfacing repeated API errors to a proactive user support/notification system).
