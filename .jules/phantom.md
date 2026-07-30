## 2025-01-15 — Global Request Coalescing for Fetch
**Gap found:** Multiple React components (like sidebars, dashboards, and maps) fetching the exact same API endpoints independently and simultaneously, causing redundant network traffic and server load.
**Why it existed:** Components were designed independently without a centralized state or data-fetching layer (e.g. SWR or React Query), relying on raw `fetch` on component mount.
**Built:** A global `window.fetch` interceptor injected via `PhantomProvider` in the root layout. It implements request coalescing (in-flight deduplication). If a fetch is already in flight for a specific URL and method, subsequent fetches return the same promise (cloning the response to avoid read locks).
**Hot path affected:** Application-wide client-side data fetching, particularly on complex pages like dashboards and scanners with many distinct widgets.
**Measurable improvement:** Reduces redundant network requests on heavy page loads by merging identical simultaneous `fetch` calls into a single network request.
**Next opportunity:** Implement a true SWR (stale-while-revalidate) cache layer on top of the coalescing interceptor to serve immediate cached responses while silently refreshing in the background.
