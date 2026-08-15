## 2024-05-18 — Predictive Pre-computation for SMS Scanner
**Gap found:** The SMS scanner was waiting for the user to explicitly click the "ANALYZE SMS ->" button before initiating the API call to the backend.
**Why it existed:** It was a naive implementation that didn't take advantage of the idle time while the user is typing or after they select a pre-defined sample text.
**Built:** The "Oracle" infrastructure module (`lib/oracle.ts`) with predictive intelligence & promise caching that debounces inputs by 500ms and pre-fires the `POST /api/analytics/scan` backend API endpoint. The promise is cached, allowing the main `handleAnalyze` call to retrieve it instantly.
**Hot path affected:** The primary scanning flow in `app/sms-scanner/page.tsx` on every user text input.
**Measurable improvement:** Reduces the perceived latency from waiting for a full `POST` request to near 0ms (cache hit) upon clicking the Analyze button.
**Next opportunity:** Expand the Oracle module's pre-computation logic to other inputs like the Phone Number search to prefetch details.
