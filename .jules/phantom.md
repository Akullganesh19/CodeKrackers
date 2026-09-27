## 2024-XX-XX — [Infrastructure Request Coalescing and Global API Interception]
**Gap found:** Multiple React components independently call `fetch()` on mounting (especially analytics/dashboard components). When a page with multiple components loads, duplicate un-cached network requests hit the server simultaneously for the exact same resource. No global caching or deduplication on `fetch`.
**Why it existed:** Developers used standard React patterns (`useEffect` + `fetch`) without a centralized HTTP client or React Query/SWR library, resulting in naive, un-coalesced requests.
**Built:** A global `window.fetch` override using request coalescing (deduplication of in-flight requests) and a short-lived `stale-while-revalidate` in-memory predictive cache for GET requests.
**Hot path affected:** Every component that does a data fetch on load (Dashboard, ScammerMap, Call Monitor analytics, etc.).
**Measurable improvement:** Reduces duplicate simultaneous API calls to exactly 1 request. Eliminates latency on repeated fast navigation or frequent polling by serving from cache instantly while validating in background.
**Next opportunity:** Background sync queues for non-critical POST mutations like telemetry or logging.
