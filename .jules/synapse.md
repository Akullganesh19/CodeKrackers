## 2025-02-14 — Scams Avoided -> User Safety Core Connection
**Systems connected:** Analytics (Threats) ↔ Users (Auth/Profiles)
**Intelligence emerged:** The User Profile now natively understands how resilient a user is against real-world scams. When the Analytics system blocks/detects a threat directed at a user, the user's `scams_avoided` counter increments and their `safety_score` dynamically adjusts, allowing the system to identify the most targeted and the most resilient users in real-time.
**Data flows:** `threat.detected` event emitted by Analytics (`/scan` and `/scan-voice`) -> triggers User Profile updates in `user_intelligence`.
**Coupling approach:** Event Bus pattern (`backend/core/event_bus.py`). Neither system imports the other's business logic, they communicate entirely via the shared event bridge.
**Next connection:** Errors ↔ Users (Link known Python exceptions directly to the user sessions experiencing them for proactive notification).
