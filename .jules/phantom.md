## 2025-03-01 — Request Coalescing and Caching Layer

**Gap found:** Components in hot paths (dashboard, analytics, OpenClawStatus) were making independent `fetch` calls without any caching or request deduplication.
**Why it existed:** The frontend components were written independently and likely developed quickly for a hackathon/MVP, prioritizing functionality over optimized data fetching.
**Built:** A `phantomFetch` wrapper around the native `fetch` API. It implements a global, in-memory request coalescing map (to dedup simultaneous calls for the same resource) and a TTL-based cache. It securely hashes headers into the cache key and gracefully handles cloning `Response` objects to avoid "body already read" errors. Instrumentation logging was added to measure cache hits and coalescing.
**Hot path affected:** Every interval refresh on the Dashboard and initial renders of Analytics and Sidebar.
**Measurable improvement:** Redundant simultaneous fetches to `/api/analytics/dashboard-summary` are eliminated. Subsequent fetches within 60 seconds are served instantly from memory with zero network latency. Console logs show `[Phantom] Cache hit` and `[Phantom] Request coalesced`.
**Next opportunity:** Implement a persistent, localized background sync queue for non-critical writes (e.g., dismissing notifications) so they are resilient to network drops.
