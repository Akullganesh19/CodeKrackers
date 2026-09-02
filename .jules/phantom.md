## 2024-05-30 — Global Request Coalescing

**Gap found:** Multiple React components (e.g., Sidebar, Maps, Analytics pages) make naive, overlapping API calls to the same endpoints simultaneously on page load without deduplication.
**Why it existed:** Components were designed in isolation, and the frontend architecture lacked a centralized data fetching layer or deduplication mechanism for parallel component mounting.
**Built:** A client-side global `window.fetch` interceptor (`PhantomInfrastructure`) that implements request coalescing. It caches in-flight promises based on the URL and headers, so concurrent identical requests share a single network call. It properly clones the response for multiple consumers.
**Hot path affected:** Initial page loads across all dashboards and analytics views where multiple widgets request aggregate data simultaneously.
**Measurable improvement:** Significantly reduces network thrashing and duplicate backend processing, saving multiple redundant HTTP requests per page view.
**Next opportunity:** Implement a stale-while-revalidate caching layer for infrequently changing dashboard reference data.
