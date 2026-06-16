## 2024-05-18 — Request Coalescing and API Caching
**Gap found:** Components were making duplicate API calls independently (e.g., polling `dashboard-summary` independently, re-fetching identical config on mount) without connection sharing or intelligent caching.
**Why it existed:** A naive approach to component data fetching in React where each component individually fetches the data it needs, resulting in a thundering herd on page load or polling boundaries.
**Built:** A `FetchOptimizer` infrastructure layer that intercepts `fetch` calls. It introduces Request Coalescing (multiple identical in-flight requests are merged into one network call) and an Intelligent Cache Layer (5-second TTL) for all `GET` requests.
**Hot path affected:** Every client-side API `GET` request in the entire app, especially high-frequency polling endpoints like `dashboard-summary`.
**Measurable improvement:** Reduces redundant network hits to `0` for duplicate simultaneous requests and serves fresh-enough data (< 5s old) from cache instantly, drastically reducing backend load and perceived latency. Added `window.phantomMetrics` to track `coalesced` and `cacheHits`.
**Next opportunity:** Edge caching headers on static assets and backend endpoints, or background queue for non-critical telemetry logs.
