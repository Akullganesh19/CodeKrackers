## 2024-06-29 — [phantomFetch: Request Coalescing and SWR Caching]
**Gap found:** The frontend components (e.g., Dashboard, Analytics) were using native `fetch` which lacked caching or request deduplication. Multiple identical queries fired concurrently on mount/reload.
**Why it existed:** Native `fetch` does not have built-in coalescing or query caching without external libraries (like React Query or SWR).
**Built:** Created `app/lib/fetch.ts` implementing `phantomFetch`. It coalesces identical requests and implements a Stale-While-Revalidate pattern with TTL and memory limits.
**Hot path affected:** Core data dashboards, including the main overview, threat map, and SMS scanner sidebar.
**Measurable improvement:** Reduced duplicate backend calls on mount, instant UI renders on return visits via local memory caching.
**Next opportunity:** Expand the caching logic to support optimistic updates for common mutation pathways.
