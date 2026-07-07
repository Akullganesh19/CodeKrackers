## 2024-10-18 — [Request Coalescing & TTL Cache Utility]
**Gap found:** Multiple components in the application independently fetched the same endpoint concurrently (e.g., dashboard summaries, admin stats) leading to redundant network calls and wasted throughput. Additionally, background fetches silently failed without returning fallback Responses.
**Why it existed:** The app was built rapidly using naive native `fetch` calls scattered across individual React component lifecycles without a centralized API client or global state management for network requests.
**Built:** A `phantomFetch` wrapper around the native `fetch` API (`app/lib/fetch.ts`) that features in-memory request coalescing to deduplicate concurrent requests for the same URL, TTL-based caching, and a stale-while-revalidate mechanism.
**Hot path affected:** Critical user-facing dashboards and admin pages where components simultaneously load analytical summary data.
**Measurable improvement:** Drastic reduction in duplicate network requests during initial page loads and component mounts. Immediate UI rendering due to serving stale cache while the background refresh resolves.
**Next opportunity:** Expand the background refresh mechanisms into a generic job queue or service worker to improve offline capabilities.
