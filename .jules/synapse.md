## 2025-05-08 — Analytics Login Correlation
**Systems connected:** [Auth ↔ Analytics]
**Intelligence emerged:** [Analytics now knows when users log in, correlating authentication activity with user roles]
**Data flows:** [Auth emits 'user.login' events with user data; Analytics subscribes and logs/tracks it]
**Coupling approach:** [Event Bus pattern. Auth and Analytics do not import each other. Both only depend on a thin EventBus in `backend/core/events.py`.]
**Next connection:** [Errors ↔ Users]
