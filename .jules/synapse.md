## 2025-05-08 — Threat Intel ↔ Auth/User Engagement
**Systems connected:** SpamShield (Threat Intel) ↔ Auth (User Session) & User Profile
**Intelligence emerged:**
1. Proactive users are now rewarded: When SpamShield blocks a threat, it updates the user's `scams_avoided` count.
2. Security monitoring now sees credential attacks: When Auth locks an account due to brute-force OTP/password failures, it logs a `Threat` in the database.
**Data flows:**
- SpamShield → User Profile (`threat.blocked` event)
- Auth → Threat Ledger (`auth.account_locked` event)
**Coupling approach:** A loosely coupled `EventBus` in `backend/core/events.py` acts as the intermediary. Systems only emit events and do not import each other. `backend/core/synapse.py` listens to these events and executes the cross-system logic.
**Next connection:** Wire Analytics to User Profile to identify feature usage drops.
