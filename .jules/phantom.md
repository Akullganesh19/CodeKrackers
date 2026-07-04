## $(date +%Y-%m-%d) — Intelligent Cache Layer & Request Coalescing
**Gap found:** Components were directly making `fetch` calls without any request deduplication, meaning if multiple components needed the same data at the same time, multiple identical network requests were dispatched. Caching was non-existent on the frontend, relying entirely on the server.
**Why it existed:** Native `fetch` lacks built-in request deduplication (coalescing) and client-side stale-while-revalidate caching. Building quick UI features usually bypasses infrastructure setup like API caching wrappers.
**Built:** Created `phantomFetch` in `app/lib/fetch.ts`, replacing all direct `fetch` calls across the app. This wrapper provides:
1. **Request Coalescing:** Uses an `inFlight` Map so simultaneous duplicate requests return the same Promise instead of duplicating network IO.
2. **Stale-while-revalidate Caching:** Employs a memory cache with TTL. When data is requested, it serves hot from the cache. If older than 30s, it serves from cache and fetches fresh data in the background silently.
**Hot path affected:** Dashboard data, analytics metrics, profile and config fetches on common views.
**Measurable improvement:** Multiple identical simultaneous requests yield 1 single network request. Caches eliminate network roundtrips completely on navigation between pages inside TTL.
**Next opportunity:** Expand with IndexedDB for cross-session persistent cache, or a prioritized offline queue for mutating API calls (background sync).
