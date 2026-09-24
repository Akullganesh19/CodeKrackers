## 2024-09-24 — Request Coalescing and Intelligent Caching Layer
**Gap found:** The frontend application makes multiple identical API calls within the same page lifecycle and fails to cache any responses, leading to redundant requests hitting the backend unnecessarily.
**Why it existed:** The native `window.fetch` implementation was used directly without any request deduping, debouncing, or background caching wrappers.
**Built:** A `window.fetch` interceptor (`lib/phantom.ts`) initialized at the layout root that coalesces in-flight GET requests and implements a 5-minute memory cache with a 30-second Stale-While-Revalidate background sync.
**Hot path affected:** Every component calling `fetch()` for data fetching, including dashboards, maps, and component renders triggered by navigation.
**Measurable improvement:** Reduces redundant network latency to zero for duplicated and recently cached requests. Consolidates multi-component concurrent fetch requests into a single network connection.
**Next opportunity:** Background queue for optimistic POST request updates with a unified outbox sync mechanism.
