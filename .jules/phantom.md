## 2024-07-14 — phantomFetch (Request Coalescing, Retry, and TTL Caching)
**Gap found:** The frontend components (Dashboard, Analytics, SMS Scanner, Call Monitor) naively hit `fetch()` directly, lacking any request coalescing, built-in caching, or automatic retries. Components making simultaneous calls on render led to duplicate requests, wasting network resources and server load.
**Why it existed:** Native `fetch` is simple and often used out-of-the-box in basic setups. The app lacked an abstracted network layer to optimize requests before they leave the client.
**Built:** Created `phantomFetch` in `@/app/lib/fetch.ts`, an invisible fetch wrapper that intercepts native calls. It performs:
1) **In-Flight Deduplication:** Coalesces identical GET requests running concurrently (e.g. 5 identical calls become 1 network request).
2) **TTL Caching:** Caches GET requests transparently for dashboard components to prevent spamming the backend during component remounts.
3) **Exponential Backoff:** Configurable automatic retries for transient failures.
**Hot path affected:** Every client-side API call across the platform, including page mounts (`/dashboard`, `/analytics`, `/sms-scanner`, `/call-monitor`).
**Measurable improvement:** Reduced redundant network traffic on concurrent component renders; increased perceived app speed via instantaneous cache hits on frequently accessed data; added robust retry logic to mask network instability from the user without altering UI.
**Next opportunity:** Stale-while-revalidate for background updates or optimistic updates in interactive components.
