## 2024-05-24 — Request Coalescing Interceptor
**Gap found:** Multiple identical API requests were being made simultaneously (e.g., from components repeatedly fetching the dashboard summary on mount or polling) with no request coalescing.
**Why it existed:** Native `fetch` operates independently, and Next.js client components often mount concurrently or fetch identical data without a shared state manager or caching layer.
**Built:** An invisible, global Request Coalescing interceptor (`PhantomInit`) that monkey-patches `window.fetch` to deduplicate simultaneous GET requests using an `inFlight` Map.
**Hot path affected:** All data-fetching components across the application (dashboards, maps, analytics).
**Measurable improvement:** Redundant simultaneous requests are intercepted and share the same underlying Promise, saving network throughput and reducing backend load. Measurable via `window._phantomSavedRequests`.
**Next opportunity:** Implement stale-while-revalidate background sync for non-critical dashboard metrics.
