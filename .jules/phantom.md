## 2025-03-09 — Request Coalescing
**Gap found:** Identical API calls made multiple times within one page load, wasting throughput and causing unnecessary UI latency.
**Why it existed:** Components fetched their data independently without an orchestration layer.
**Built:** An invisible request coalescer that monkey-patches `window.fetch` to deduplicate identical in-flight GET requests.
**Hot path affected:** All client-side fetch requests.
**Measurable improvement:** Reduces duplicate network requests on page loads and complex component renders.
**Next opportunity:** Edge caching for static assets.
