## 2024-05-08 — Account Lockout Threat Intel Connection
**Systems connected:** Auth ↔ Threat Intel / Audit
**Intelligence emerged:** When a user account is locked due to brute force login attempts, the system automatically surfaces this security event by logging it into the forensic Audit log and adds the offending client IP address to the Community Blacklist. This proactively protects the platform by integrating authentication failure intelligence with the threat identification mechanisms.
**Data flows:** Auth System (failed login attempts, user ID, IP Address) -> Event Bus -> Audit System (records event) & Threat Intel (blacklists IP).
**Coupling approach:** Event Bus pattern (`backend/core/events/bus.py`). The Auth system emits an `account_locked` event. The Event Bus relays this to the Threat Intel/Audit listeners without tightly coupling the systems. Neither system imports the other.
**Next connection:** Correlate user reported scams (from FIR system) with their Threat scoring history to fine-tune the threat severity detection models based on user demographics.
