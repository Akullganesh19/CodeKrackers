## 2025-06-25 — Brute Force Threat Correlation
**Systems connected:** Auth ↔ Threats
**Intelligence emerged:** The Analytics/Threat system now automatically logs and categorizes repeated failed authentication attempts as OTP_FRAUD threats, providing visibility into brute-force attacks which previously only the Auth system knew about.
**Data flows:** When an account hits `MAX_LOGIN_ATTEMPTS` (in `/verify` or `/login`), Auth emits an `auth.failed_login_limit_reached` event via the new Event Bus. The listener creates a `Threat` with severity MEDIUM and ties it to the user's email and IP address.
**Coupling approach:** The implementation uses an in-memory `EventBus` (`backend/core/events/bus.py`). Auth publishes events without knowing who listens, and the Threat service subscribes asynchronously. Neither system imports the other directly.
**Next connection:** Correlating User Safety Scores with Gamification or Spam Blocking.
