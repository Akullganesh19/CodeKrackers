## 2025-06-24 — Request Coalescing and Stale-While-Revalidate Cache

**Gap found:** The frontend application makes duplicate API requests to identical endpoints (especially on page load across multiple components) without coalescing them. There was no caching on the frontend layer.
**Why it existed:** The native `fetch` API does not automatically coalesce requests or cache responses in a simple way without a dedicated client library (like SWR or React Query), so developers often build components that naively fetch their own data independently.
**Built:** A `dedupedFetch` utility in `app/lib/api.ts` that coalesces identical in-flight GET requests and implements an in-memory Stale-While-Revalidate (SWR) caching pattern with a 30-second TTL.
**Hot path affected:** Every component that reads API data heavily, especially the `Sidebar.tsx` fetching safety metrics repeatedly across page changes.
**Measurable improvement:** Multiple identical requests are now batched into a single network call. Cached data is served instantly while background revalidation updates the cache.
**Next opportunity:** Implement a robust offline queue for write requests.
