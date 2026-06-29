## 2025-06-29 — Auth Lockout Threat Detection
**Systems connected:** Auth ↔ Threats/Analytics
**Intelligence emerged:** The Threat system now automatically detects and records brute force or credential stuffing attacks when users get locked out by the Auth system. This allows security operators to see localized attacks and correlate them with other fraud signals.
**Data flows:** Auth system's account lock events (`user.account_locked`) stream directly to the Threats system, including IP address, identifier, and attempts, which are captured as new `Threat` records.
**Coupling approach:** The connection is built using a globally registered Event Bus (`backend/core/events/bus.py`). The Auth module only imports the bus to publish events, completely decoupled from Threat schemas or logic. The listener (`backend/core/events/listeners.py`) catches the event and manages writing to the database independently.
**Next connection:** I should wire the user's `ScoreHistory` drops into an automated Slack/Email alert so operators can intervene for rapidly decreasing safety scores before fraud fully materializes.
