## 2024-09-28 — Global Request Coalescing (Fetch Interceptor)

**Gap found:** Multiple React components (e.g., `Dashboard`, `Analytics`, `ScammerMap`, `Sidebar`) independently call `fetch()` on the same endpoints (like `/api/analytics/dashboard-summary` and `/api/analytics/threat_map`) simultaneously or in quick succession when rendering the UI.
**Why it existed:** Components were written to be self-contained and independently fetch the data they need on mount using `useEffect`, without a global state manager (like Redux, React Query, or SWR) to deduplicate simultaneous requests for the same resource.
**Built:** A global `window.fetch` interceptor in a Next.js `ClientProvider` that introduces Request Coalescing. It intercepts all outgoing `fetch` calls. If a request with the same method and URL is already in-flight, it returns the existing Promise instead of opening a new network connection.
**Hot path affected:** Every page load that aggregates multiple widgets, particularly the Analytics and Dashboard views, which both request `dashboard-summary`.
**Measurable improvement:** Reduces redundant network requests on initial page load by coalescing identical concurrent `GET` requests into a single network call.
**Next opportunity:** Implement stale-while-revalidate caching layer with background sync.
