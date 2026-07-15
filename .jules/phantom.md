## 2025-02-18 — Request coalescing and caching layer

**Gap found:** The frontend components were making multiple naive, overlapping `fetch` calls to the same endpoints simultaneously, especially on mount, without any deduplication, caching, or automatic retry logic.
**Why it existed:** The app was built quickly using standard `fetch` without an overarching client-side state management or query library (like React Query or SWR).
**Built:** `phantomFetch` in `app/lib/fetch.ts`, a centralized, invisible wrapper around native `fetch`. It includes:
1. In-flight request coalescing (preventing duplicate simultaneous requests).
2. A TTL-based cache layer with stale-while-revalidate for GET requests.
3. Automatic exponential backoff retries for transient HTTP errors.
**Hot path affected:** Every client-side component making API calls (Dashboard, Analytics, Maps, Topbars). Users feel it as instantaneous navigation and zero-latency component mounts.
**Measurable improvement:** Reduced redundant network requests (observable in browser network tab) and eliminated layout jank caused by staggered loading states.
**Next opportunity:** Implement a predictive prefetcher (Oracle) that primes the `phantomFetch` cache before the user clicks on links or elements.
