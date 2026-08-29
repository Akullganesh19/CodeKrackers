## 2024-05-19 — Request Coalescing

**Gap found:** The frontend components independently fetched identical APIs (e.g., dashboard summaries, scanning scores, blocklists) on load and interactions without coordinating, leading to redundant parallel network requests.
**Why it existed:** Native `fetch()` calls were scattered across individual Next.js client components without a shared caching or deduplication layer.
**Built:** A global `window.fetch` interceptor in `PhantomProvider.tsx` that coalesces identical simultaneous GET requests by storing the active Promise in an `inFlight` Map. Duplicate callers now await the same initial request and receive a cloned Response to avoid stream consumption errors.
**Hot path affected:** Initial page loads, dashboard navigations, and concurrent widget updates.
**Measurable improvement:** Reduces the number of outbound API requests by deduplicating overlapping calls, lowering backend load and frontend network latency.
**Next opportunity:** Stale-while-revalidate background caching for less-frequently updated intelligence data like safety scores.
