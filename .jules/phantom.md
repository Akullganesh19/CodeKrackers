## 2024-06-21 — [Request Coalescing for Frontend Fetch]
**Gap found:** The frontend `window.fetch` implementation was naive. Multiple components on the same page rendering simultaneously could trigger duplicate identical GET requests, wasting network bandwidth and backend processing.
**Why it existed:** Next.js and React often result in multiple components requesting the same data on mount. Without a centralized caching or coalescing strategy, each component fires its own request independently.
**Built:** A global `window.fetch` interceptor (`lib/fetch.ts`) initialized via `app/client-layout.tsx` that coalesces simultaneous identical GET requests. If multiple requests for the same URL are fired in the same tick, only one actual network request goes out. The rest wait for the single Promise to resolve and return cloned responses.
**Hot path affected:** Any page load where multiple components request the same data (e.g., user profiles, settings, unread counts).
**Measurable improvement:** Reduces redundant network requests on initial page loads and complex client-side navigations. Inspecting the Network tab will show only one request per unique GET URL per event loop tick.
**Next opportunity:** Investigate API response caching (stale-while-revalidate) or intelligent prefetching based on user hover states.
