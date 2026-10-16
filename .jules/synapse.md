## 2024-05-18 — Threat Resolutions Inform User Metrics & Audits
**Systems connected:** Threats ↔ Users (Analytics) & Audit
**Intelligence emerged:** When a threat's status is changed to resolved, we now know the user successfully avoided a scam. We can track this metric (scams_avoided) over time for each user. Simultaneously, threat status changes are now correctly entering the immutable audit log for compliance.
**Data flows:** Threats system emits `threat.status_changed`. The Intelligence (Synapse) layer listens, writes to the Audit log, and if the threat is resolved, it updates the owner's `scams_avoided` metric in the Users system.
**Coupling approach:** Event Bus pattern (`backend/core/events.py`). The threats API does not import the audit service or the users models. It just fires `await event_bus.emit("threat.status_changed", ...)`. The new `backend/services/intelligence.py` listens to this event and coordinates the updates.
**Next connection:** Correlate FIR generations with user threat patterns to identify repeat victims.
