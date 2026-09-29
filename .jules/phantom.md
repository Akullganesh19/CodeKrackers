## 2025-02-28 — Global Request Coalescing & Intelligent Caching Layer

**Gap found:** The application was making redundant, overlapping `fetch` requests across different components. In places like `Analytics`, `Dashboard`, and `Call Monitor`, components mount and hit the exact same endpoints (e.g., dashboard summaries, threat maps, or status endpoints). The naive `fetch` infrastructure simply sent a request to the server every time `fetch` was called, serializing work and hammering the backend.

**Why it existed:** Native Next.js/React development frequently leads to disconnected components managing their own data fetching using `useEffect`, which naturally results in independent duplicate API calls if no global state manager like React Query or SWR is used.

**Built:** `PhantomProvider`, an invisible root-level infrastructure component that intercepts all native `window.fetch` calls. It introduces two major improvements:
1. **Request Coalescing:** Identical simultaneous requests are collapsed into a single network call. If component A calls `/api/data` and component B calls it 10ms later, B receives the exact same promise from A without hitting the network again.
2. **Edge Caching Layer:** Caches GET requests for 30 seconds using an in-memory blob cache. Any requests made within that TTL return the cached response immediately (stale-while-revalidate pattern), drastically reducing latency on read-heavy routes.

**Hot path affected:** Every single client-side data fetch in the application. Particularly noticeable on dashboard load where multiple metrics/charts fetch data simultaneously, or navigating between pages that share data sources.

**Measurable improvement:** Multiple overlapping requests to the same endpoint now result in exactly 1 network call instead of N. Subsequent navigations to already-fetched data resolve in 0ms network latency.

**Next opportunity:** Background Sync queues for POST/PUT requests (e.g. submitting reports/evidence), to allow optimistic UI updates while the actual network call happens safely in the background with retry logic.
