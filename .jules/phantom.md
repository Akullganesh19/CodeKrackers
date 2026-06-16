## 2024-05-24 — Request Coalescing

**Gap found:** Multiple components on dashboards independently trigger `fetch()` for the exact same data (`/api/analytics/dashboard-summary` and `/api/analytics/threat_map`) simultaneously on page load. No request deduplication existed.
**Why it existed:** Native React components developed in isolation often fetch their own dependencies without a centralized state manager (like React Query), causing a "thundering herd" of identical network requests to the backend.
**Built:** A global `window.fetch` interceptor (`lib/fetch.ts`) acting as an invisible infrastructure layer. It maps in-flight GET requests by URL + Authorization header and returns cloned promises to multiple callers, effectively coalescing identical simultaneous requests into a single network call.
**Hot path affected:** Initial dashboard page load and navigation across components that require analytical data.
**Measurable improvement:** On the main analytics dashboard load, the number of `/api/analytics/dashboard-summary` GET requests is reduced from N (where N is the number of mounted components requesting it) to exactly 1.
**Next opportunity:** Implementing an intelligent Edge Cache or Service Worker for offline capability and background sync.
