## 2023-10-24 — Global Fetch Coalescing and Caching
**Gap found:** Components were naively making identical, overlapping `fetch` requests (e.g., `dashboard-summary` from both the main dashboard and the sidebar simultaneously, or repeated map polling).
**Why it existed:** Different components needed the same data but lacked a centralized store or caching layer, relying on independent intervals and effect hooks.
**Built:** A global `window.fetch` interceptor that coalesces simultaneous identical GET requests into a single network call and provides a short-lived (2s) memory cache (`stale-while-revalidate` style) to prevent rapid re-fetching during component mounts and re-renders.
**Hot path affected:** Every client-side API call made via `fetch` across the entire React application.
**Measurable improvement:** Reduces duplicate network requests on page load by at least 50% for shared data (like dashboards and sidebars) and eliminates thundering herd problems when multiple components mount simultaneously.
**Next opportunity:** Implement persistent caching (e.g., indexedDB) for static reference data (like lists of known scam vectors) or background prefetching for predictable user navigation paths.
