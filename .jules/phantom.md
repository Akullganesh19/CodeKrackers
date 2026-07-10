## 2024-05-18 — Request Coalescing and In-Memory Caching (phantomFetch)
**Gap found:** The frontend components independently trigger identical background HTTP calls to analytics and mapping endpoints without deduplication.
**Why it existed:** Native `fetch` does not coalesce identical requests or implement caching automatically. Each component that mounts triggers its own fetch, leading to network spam and wasted bandwidth.
**Built:** A drop-in replacement global fetch utility (`phantomFetch`) located in `app/lib/fetch.ts` that provides request coalescing (deduping) and a short-lived 5-second in-memory TTL cache to survive component unmounts and serve hot-path data instantly.
**Hot path affected:** Dashboard analytics summaries, spatial threat maps, safety scores, and other frequently polled endpoints during component mounting or interval polling.
**Measurable improvement:** Multiple identical simultaneous GET requests are coalesced into a single network call. Component re-mounts within 5 seconds perceive zero latency by reading from the memory cache instead of re-fetching.
**Next opportunity:** Expand background data syncing using Stale-While-Revalidate caching pattern for the background service worker or implement predictive prefetching for anticipated navigation flows.
