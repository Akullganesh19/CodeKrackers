## 2025-05-08 — Scam Avoidance Gamification
**Systems connected:** Spam Shield (Detection) ↔ User Profile (Gamification/Auth)
**Intelligence emerged:** The user profile now tracks exactly how many scams the user has been protected from. When a spam message or call is blocked, the user's `scams_avoided` count is incremented in real-time, providing measurable security value and gamification.
**Data flows:** `backend/services/spam_shield.py` evaluates the risk score. If the action is `SpamAction.BLOCK`, it publishes a `spam.blocked` event containing the `user_id`. The main application startup in `backend/main.py` subscribes to this event, catching it and incrementing `User.scams_avoided` in the database without direct cross-module imports.
**Coupling approach:** Event Bridge Pattern (`backend/core/event_bus.py`). The Spam Shield knows nothing about gamification, and the Gamification/User module knows nothing about how spam is blocked.
**Next connection:** Correlate error logs in monitoring with specific user segments (e.g. Error ↔ User Profile) to proactive alert high-value users when they encounter issues.
