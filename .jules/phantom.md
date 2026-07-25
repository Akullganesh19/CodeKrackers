## 2025-02-27 — Global fetch request coalescing and SWR caching
**Gap found:** Native, un-cached multiple fetch requests were executed directly inside client components, potentially triggering duplicate requests on rerenders or parallel components accessing the same data, wasting bandwidth and adding latency.
**Why it existed:** Using standard frontend practices without a central data fetching library like React Query or SWR, relying instead on raw `fetch()` directly in effects/event handlers without a coalescing or caching mechanism.
**Built:** A global `window.fetch` wrapper client component (`PhantomInfrastructure.tsx`) that implements request deduplication via an `inFlight` map and an intelligent Stale-While-Revalidate (SWR) cache layer.
**Hot path affected:** Every client-side fetch request executed via `window.fetch`. Users will perceive instantaneous navigation and rendering for repeated data requests.
**Measurable improvement:** Prevents duplicate active network calls to the same endpoint simultaneously. Repeated data fetches are instantly fulfilled from the cache, followed by an invisible background sync.
**Next opportunity:** Investigate pre-fetching mechanisms driven by user intent (e.g. hovering over navigation links).
