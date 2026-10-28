## 2024-10-28 — Login Analytics Correlator
**Systems connected:** Auth ↔ Analytics
**Intelligence emerged:** Correlating auth login events directly into analytics dashboards gives real-time visibility into application usage patterns without the overhead of heavy db queries.
**Data flows:** When `backend/api/auth.py` processes a successful login, it fires an asynchronous `user.login` event via an event bus (the `EventBus` class in `backend/core/events.py`). The `backend/api/analytics.py` script subscribes to this bus and increments a lightweight in-memory login counter (`login_metrics["total_logins_today"]`) and timestamps the last login, making these metrics instantly queryable.
**Coupling approach:** Event Bridge Pattern - A pub/sub mechanism is utilized, decoupling the source from the destination. `Auth` and `Analytics` are completely unaware of one another and do not import each other.
**Next connection:** Errors ↔ Users (to proactively track users encountering errors).
