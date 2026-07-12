## 2024-07-12 — Global Fetch Coalescing and Caching
**Gap found:** The frontend components were blindly using naive `fetch` calls, which meant multiple components requesting the same API endpoints (e.g. analytics dashboards, status badges) would duplicate concurrent requests and wait on the network unnecessarily.
**Why it existed:** It was a naive default React implementation that lacked an infrastructure layer.
**Built:** A globally accessible caching wrapper called `phantomFetch` that checks a `globalCache` of in-flight promises and resolved responses based on serialized Request objects, passing non-GET requests immediately, coalescing concurrent GETs, and avoiding caching of errors.
**Hot path affected:** Any GET request in Next.js frontend (components fetching dashboards, analytics maps, status widgets).
**Measurable improvement:** Prevented duplicate network connections during component mounts and re-renders, collapsing thundering herds into a single fetched promise.
**Next opportunity:** Background optimistic UI state syncing for offline capability.
