## 2025-02-05 — Request Coalescing (In-flight Deduplication)

**Gap found:** The frontend lacked any mechanism to prevent redundant concurrent API requests. Multiple components rendering simultaneously could fire off identical `fetch` requests (e.g., fetching dashboard summaries, analytics, or user profiles repeatedly), wasting network bandwidth and backend compute.

**Why it existed:** The native `fetch` API does not automatically coalesce concurrent requests for the same resource. Without a state management library like React Query or SWR configured for coalescing, Next.js client components will redundantly fetch the same endpoints on mount.

**Built:** A global `PhantomProvider` that intercepts `window.fetch`. It introduces request coalescing (in-flight deduplication) using an `inFlightRequests` Map. If a `GET` request is fired while an identical request is already pending, it returns a clone of the original promise's response, completely bypassing the network.

**Hot path affected:** Every client-side data fetch across the entire application (dashboard loads, map renders, analytics panels).

**Measurable improvement:** Reduces redundant network requests on heavy page loads by up to 100% for identical endpoints (e.g., if 3 components fetch the same summary data, only 1 network request is made). Reduces backend load and perceived latency.

**Next opportunity:** Implement Stale-While-Revalidate (SWR) caching layered on top of the request coalescing for instant data loads on subsequent navigations.
