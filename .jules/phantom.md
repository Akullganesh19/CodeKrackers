## 2025-02-20 — Request Coalescing and Stale-While-Revalidate Caching Layer
**Gap found:** Native `fetch()` calls scattered across components lacked deduplication and caching. Identical GET requests on the same page load hit the server redundantly. Background refresh blocked or wasn't implemented smoothly.
**Why it existed:** Quick implementation of endpoints led to standard direct fetching per component, ignoring network optimization and request lifecycle management.
**Built:** `phantomFetch` (`app/lib/fetch.ts`) — An invisible wrapper over standard `fetch` that provides immediate request coalescing (deduplication of simultaneous requests for the same URL) and Stale-While-Revalidate caching with size-based LRU eviction.
**Hot path affected:** Every client-side GET request (e.g., `dashboard-summary`, `safety-score`, `scan-voice`, `threat_map`).
**Measurable improvement:** Significantly reduced redundant network calls by coalescing simultaneous fetches and caching previous responses for instantaneous rendering on frequent navigation paths.
**Next opportunity:** Implement a robust background job queue for heavy sync operations (e.g., image/audio processing offload) that currently block main interaction flows.
