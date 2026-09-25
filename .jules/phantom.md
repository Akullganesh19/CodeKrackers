## 2025-02-25 — Fetch Request Coalescing

**Gap found:** Multiple identical concurrent API calls for the same data (e.g., `dashboard-summary`, map layers, etc.) were being issued without deduplication due to decentralized hooks and components mounting simultaneously.
**Why it existed:** Native `fetch` lacks built-in coalescing for identical requests, and Next.js React component hierarchies typically rely on isolated `useEffect` fetches, causing the same initial network request multiple times on a single screen layout.
**Built:** A global `window.fetch` interceptor (`FetchInterceptor.tsx`) that acts as an intelligent deduplication layer for all identical `GET` requests using a shared `inFlightRequests` Map.
**Hot path affected:** Every component and hook utilizing global `fetch`, significantly across dashboard, analytics, and sidebar initialization routes.
**Measurable improvement:** Prevented duplicated API throughput directly proportionally to the number of subcomponents relying on the same API (e.g., saving `N-1` redundant requests where `N` is concurrent dependent modules).
**Next opportunity:** Investigate frontend predictive fetching/caching for search query typing or background persistent local data caching for slow networks to pair with the coalescing.
