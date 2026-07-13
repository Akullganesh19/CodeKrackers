## 2024-05-18 — [Invisible Request Infrastructure]
**Gap found:** Multiple components making raw, independent `fetch` calls to the same API endpoints simultaneously, causing duplicate network requests and waiting for synchronous network operations on every component mount. No retry mechanism for transient failures.
**Why it existed:** Simple direct use of standard `fetch` API without a centralized caching or state layer.
**Built:** `phantomFetch`, a wrapper around `fetch` offering automatic request coalescing (in-flight deduplication), transparent TTL caching, and exponential backoff retries. We seamlessly patched all `.tsx` and `.ts` files to use `phantomFetch` instead of standard `fetch`.
**Hot path affected:** Every client-side component loading state, particularly dashboard summaries and analytics maps which previously requested the same data multiple times on load.
**Measurable improvement:** Redundant network requests on page load reduced to 1 per endpoint, eliminating N-1 requests. Cached endpoints resolve in < 1ms on subsequent navigations within the TTL window. Automatic retries on transient errors hide network blips from the user.
**Next opportunity:** Implement stale-while-revalidate for background refreshing of cached data without blocking render.
