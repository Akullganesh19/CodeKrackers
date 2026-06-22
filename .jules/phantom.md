## 2024-05-19 — Intelligent Fetch Layer with Request Coalescing

**Gap found:** The frontend components were making naive, un-cached `fetch` calls directly to the API, including on heavily-trafficked dashboard and overview pages. Multiple components on the same page were independently fetching identical data (e.g., dashboard summaries, system status), leading to duplicate network traffic and unnecessary database load. No caching meant users endured latency on every page navigation.

**Why it existed:** The application was built rapidly for a hackathon, prioritizing functionality over frontend architecture. Components were built in isolation without a centralized API data management layer.

**Built:** Introduced `dedupedFetch` in `app/lib/api.ts`. This acts as an invisible interception layer that provides:
1. **Request Coalescing:** Multiple simultaneous requests for the exact same URL + headers are merged into a single network flight. Resolves the "thundering herd" of component-mount fetches.
2. **Short-lived Cache (TTL):** A 5-second TTL cache ensures that rapid navigations or component re-renders within a short window return instantly without hitting the network.
3. **Stale-While-Revalidate:** If cached data is getting older but hasn't expired, it returns the cache instantly while kicking off a background network request to invisibly update the cache for the next time.
4. Only `GET` requests are cached/coalesced to ensure `POST`/`PUT`/`DELETE` operations remain transactional and bypass the cache.

**Hot path affected:** Every single data-fetching operation in the dashboard, analytics, sms-scanner, and call-monitor pages.

**Measurable improvement:** Page transitions on the frontend will no longer block on repeated data fetches. Network waterfalls on dashboard mounts are reduced by merging identical requests. The frontend now operates noticeably snappier for users.

**Next opportunity:** Implement aggressive pre-fetching on hover events for navigation links to prime the `dedupedFetch` cache before the user even clicks.
