## 2024-06-27 — Request Coalescing & Edge Cache
**Gap found:** Multiple React components (like Sidebar, Dashboard, Analytics map) made identical overlapping `fetch()` requests for the same analytical summary data, threat maps, and safety scores simultaneously on mount.
**Why it existed:** Native React components were fetching independently without a centralized state manager or request caching layer.
**Built:** Created `dedupedFetch` (`app/lib/api.ts`) wrapping native fetch with an in-flight promise tracker and a stale-while-revalidate TTL cache map.
**Hot path affected:** Navigation into Analytics, SMS Scanner, and Dashboard pages now dedupes identical GET requests transparently.
**Measurable improvement:** Reduces redundant network hits by directly returning cloned active Promises for simultaneous requests, saving latency and backend load.
**Next opportunity:** Background sync queue for non-critical telemetry or user actions (like reading notifications) to prevent UI blocking.
