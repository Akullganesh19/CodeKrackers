## 2025-05-18 — Auth Intelligence Pipeline
**Systems connected:** Auth ↔ Core/Users
**Intelligence emerged:** Correlating authentication failures and successes with user safety scores. Repeated login failures lower a user's safety score, reflecting higher risk. Successful logins gradually recover it.
**Data flows:** Auth service emits `auth.failure` and `auth.success` events with `user_id` to the Event Bus. The listener asynchronously updates the `safety_score` field in the User model.
**Coupling approach:** Event Bus pattern (`backend/core/events/bus.py`). Auth service publishes events without knowing who listens. The listener (`backend/core/events/listeners.py`) performs the database update asynchronously.
**Next connection:** Consider connecting Threat Detection with Notifications to proactively warn users when a new smishing campaign is detected locally.
