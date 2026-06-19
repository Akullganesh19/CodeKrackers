## 2025-02-23 — [Request Coalescing Interceptor]
**Gap found:** Multiple components on the same page were initiating duplicate concurrent `fetch` requests for identical resources (e.g., dashboard summaries and analytical metrics).
**Why it existed:** Components were structured independently without a centralized state or data-fetching deduplication layer, causing redundant network calls.
**Built:** A globally initialized `window.fetch` interceptor in `lib/fetch.ts` (bootstrapped via `app/client-layout.tsx`) that stores in-flight `GET` requests in a `Map`. Identical outgoing requests attach to the existing Promise instead of hitting the network.
**Hot path affected:** Any page with multiple independent widgets pulling the same server data (e.g., Analytics Dashboard, SMS Scanner views).
**Measurable improvement:** Reduces redundant backend hits. Can be measured by verifying the Network tab (or backend logs) for coalesced API calls on dashboard loads.
**Next opportunity:** Investigate an intelligent edge caching or stale-while-revalidate pattern for static backend configurations.
