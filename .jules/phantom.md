## 2025-02-20 — Request Coalescing and SWR Caching
**Gap found:** Multiple components on identical pages (Dashboard, Analytics) were repeatedly and independently calling the exact same analytics summary and threat map endpoints on every render/interval without any caching or debouncing.
**Why it existed:** The frontend used naive, raw `fetch()` calls locally inside `useEffect` blocks that executed uncoordinated network requests.
**Built:** Implemented `phantomFetch` in `app/lib/fetch.ts` to coordinate coalescing and TTL caching.
**Hot path affected:** `/dashboard` and `/analytics` rendering and interval update cycles.
**Measurable improvement:** Reduces redundant network latency to zero for multiple identical in-flight and repeated requests per user session, offloading load from the Python backend and making UI rendering immediate.
**Next opportunity:** Expand background sync capability to the threat reporting tool (`app/sms-scanner/page.tsx`).
