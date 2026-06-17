## 2024-06-18 — Spam Report Reputation Loop
**Systems connected:** Spam Shield ↔ Gamification (User Reputation)
**Intelligence emerged:** When a user reports spam, their proactive defense action is now recognized by the gamification system, automatically incrementing their `scams_avoided` counter and increasing their `safety_score`.
**Data flows:** `current_user.id` moves from the Spam Shield API boundary to the User Reputation models via an asynchronous event bus message (`spam.reported`).
**Coupling approach:** Event Bridge Pattern. The `Spam Shield` system only emits an event using the `backend.core.event_bus` without directly importing or interacting with `backend.models.user` or any reputation update logic. A separate listener (`handle_spam_reported` in `backend/core/listeners.py`) subscribes to the event and executes the update.
**Next connection:** Auth ↔ Analytics. Emitting `user.login` events to correlate login frequency with the types of threats users are encountering in the dashboard.
