## 2024-06-20 — [Request Coalescing Interceptor Added]
**Gap found:** Multiple identical GET requests being made simultaneously from various components during page load or interaction (no deduplication).
**Why it existed:** Components independently fetched data using raw `fetch` calls without a centralized caching or tracking layer.
**Built:** Global `window.fetch` interceptor (`lib/fetch.ts`) initialized via `app/client-layout.tsx` for the Next.js App Router that implements request coalescing. It stores in-flight GET request Promises in a Map and returns the existing Promise (cloned) if a matching request is already underway.
**Hot path affected:** Any page or component that fetches API data simultaneously (e.g., Dashboards, Analytics).
**Measurable improvement:** Reduces the number of identical, concurrent outbound HTTP requests, saving bandwidth and lowering server load.
**Next opportunity:** Implement stale-while-revalidate caching with TTL for frequently-read configuration or static data.
