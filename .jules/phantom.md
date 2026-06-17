## 2024-06-18 — [Request Coalescing Interceptor Added]
**Gap found:** Multiple independent components fetch identical analytical endpoints concurrently on load.
**Why it existed:** React/Next.js components mount and request data individually without shared state contexts for simple gets.
**Built:** A global `window.fetch` interceptor (`lib/fetch.ts`) that implements request coalescing. It traps concurrent GET requests to the same URL, fires only a single actual network request, and serves the cloned response to all callers.
**Hot path affected:** App load and dashboard transitions, where multiple widgets fetch overlapping summaries or status endpoints.
**Measurable improvement:** Reduces duplicate network round-trips by combining simultaneous requests. Number of pending TCP connections on load drops.
**Next opportunity:** Edge caching for static reference data (like threat intel rules) and pre-fetching adjacent dashboard views.
