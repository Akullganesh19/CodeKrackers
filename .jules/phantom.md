## 2024-10-27 — [Invisible Infrastructure Added: smartFetch]
**Gap found:** Naive API calls across the frontend (`fetch` was called repeatedly for the same data without any coalescing, caching, or deduplication, e.g. `dashboard-summary` on intervals).
**Why it existed:** Quick implementation for hackathon/prototype without deep thought into performance under load.
**Built:** An intelligent fetch wrapper (`smartFetch`) that coalesces duplicate inflight requests, caches responses, and uses stale-while-revalidate for background refreshing.
**Hot path affected:** Every single API call across the frontend (dashboard summary, maps, voice scans, reporting).
**Measurable improvement:** Reduced duplicate concurrent network requests; instant cached renders while revalidating data in background.
**Next opportunity:** Implement a prioritized queuing system for heavy background ML processing (like voice scan) so it yields to critical foreground actions.
