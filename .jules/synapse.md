## 2025-07-04 — Account Lockout Threat Intel
**Systems connected:** Auth ↔ Threat Intelligence
**Intelligence emerged:** Automatic detection and tracking of Account Takeover / Brute-force attacks when users exceed maximum login attempts.
**Data flows:** Auth system (`auth.py`) emits an `account_locked` event with user ID, identifier, and attempt count. The Event Listener (`listeners.py`) catches it and securely inserts a new Threat record into the database.
**Coupling approach:** Loosely coupled using an EventBridge pattern (`event_bus.py`). Neither system imports the other directly, and listener execution is wrapped in a `try...except` to prevent secondary system failures from crashing primary Auth flows.
**Next connection:** Errors ↔ Users (to automatically notify users when they hit known bugs).
