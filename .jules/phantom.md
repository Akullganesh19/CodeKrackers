## 2024-03-24 — Global Request Coalescing (Fetch Interceptor)

**Gap found:** Multiple components in the dashboard and layout trigger redundant `fetch()` requests for the same URLs (like `/api/analytics/dashboard-summary` or auth refreshes) simultaneously on initial load without request coalescing.
**Why it existed:** The React frontend was relying on standard, un-wrapped `window.fetch` inside `useEffect` blocks or component mount hooks across isolated components, meaning each component independently instantiated network requests.
**Built:** Created `PhantomFetch`, an invisible `<PhantomFetch />` client component that injects a global request coalescer by wrapping `window.fetch` outside the React lifecycle. It hashes requests by URL and Headers, returning cloned resolved responses (`res.clone()`) to satisfy simultaneous consumers from a single underlying flight.
**Hot path affected:** Every client-side page load (specifically the global Layout load and concurrent Dashboard summary fetches).
**Measurable improvement:** Drastic reduction of duplicate concurrent requests to identical endpoints (especially GET requests on page load).
**Next opportunity:** Edge caching for static reference data (like geospatial maps or rule definitions).