## 2024-07-05 — [Invisible Caching Layer & Request Coalescing]
**Gap found:** The application used naive `fetch` everywhere, leading to duplicate simultaneous requests for the same endpoints (lack of coalescing) and unnecessary network calls on every page navigation (no client-side caching).
**Why it existed:** Native `fetch` is stateless and oblivious to other components.
**Built:** `phantomFetch`, a drop-in replacement for the native `fetch` API. It implements request coalescing (by caching the promise itself) and a Stale-While-Revalidate (SWR) cache pattern with a 30-second TTL.
**Hot path affected:** Dashboard, Analytics, and all sidebar/map API endpoints.
**Measurable improvement:** Subsequent navigations between dashboard views happen instantly with 0ms network latency as data is served from the TTL cache. Simultaneous component mounts fetching the same resource send exactly 1 request.
**Next opportunity:** Expand phantomFetch to include request queues and backpressure mechanisms for background sync operations.
