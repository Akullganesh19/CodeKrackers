## 2026-07-08 — Invisible Fetch Wrapper (Request Coalescing & Edge Caching)
**Gap found:** Multiple components in the Next.js app were naively calling `fetch()` independently (e.g., `dashboard-summary`, `threat_map`, `safety-score`). In extreme cases, multiple identical GET requests were fired simultaneously.
**Why it existed:** Native `fetch()` in React components without a centralized data-fetching library (like SWR or React Query) doesn't deduplicate in-flight requests or cache responses automatically, causing redundant network trips and UI latency.
**Built:** `phantomFetch` (`app/lib/fetch.ts`), an invisible drop-in replacement for `fetch()` that provides request coalescing (identical in-flight requests share the same promise) and a TTL-based cache. It completely mimics the Response object api (returning `new Response` object with a `.json()` stream from cached values).
**Hot path affected:** Core analytic dashboard loads (`/analytics`, `/dashboard`, `/sms-scanner`, etc.) all now share cache.
**Measurable improvement:** Multiple components asking for `dashboard-summary` will only trigger 1 network request. Subsequent loads within the TTL are instant.
**Next opportunity:** Background sync queue for non-critical writes (like reporting spam).
