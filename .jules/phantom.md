## 2024-07-26 — Request Coalescing Interceptor
**Gap found:** Multiple React components fetching identical endpoints on page load independently (e.g., dashboard summary, map data).
**Why it existed:** Standard React architecture where disconnected components fetch their own required data without a centralized store or caching layer.
**Built:** A global `window.fetch` interceptor (`PhantomInterceptor`) injected at `app/layout.tsx` that coalesces duplicate concurrent GET requests into a single network call.
**Hot path affected:** Client-side initial page loads and component mounting.
**Measurable improvement:** Reduced network roundtrips for identical requests.
**Next opportunity:** Stale-while-revalidate client-side caching.
