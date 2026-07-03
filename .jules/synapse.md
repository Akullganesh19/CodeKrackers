## 2025-06-25 — Auth Lockout Intelligence Bridge
**Systems connected:** Auth ↔ Threat Intelligence
**Intelligence emerged:** Accounts locking out from brute-force attempts automatically feed into the platform's global Threat Intelligence system. This means if an attacker repeatedly tries to guess a password or OTP and hits the `MAX_LOGIN_ATTEMPTS` limit, their email and IP address are automatically blacklisted across the entire platform. Other users are instantly protected from that email identifier.
**Data flows:** `user_email`, `failed_attempts`, and `ip_address` move from the Authentication system to the Threat Intelligence system when a lockout event occurs.
**Coupling approach:** Event Bridge Pattern. The Auth endpoints simply emit a `user.account_locked` event onto a central `EventBus`. A separate listener, hooked up on application startup, subscribes to this event and calls `auto_blacklist` from the Threat Intelligence service. Neither system needs to directly import the other, maintaining loose coupling.
**Next connection:** Correlate user feature engagement (Analytics) with premium plan tier (Payments) to predict churn risk.
