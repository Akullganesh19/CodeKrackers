## 2024-06-19 — Request Coalescing Interceptor
**Gap found:** Multiple identical API calls were made on the frontend concurrently. The application was redundantly fetching data across different components making independent `fetch` requests for identical endpoints.
**Why it existed:** Native `window.fetch` doesn't deduplicate in-flight requests. Standard React usage patterns often lead to independent components mounting and fetching simultaneously without a shared global cache.
**Built:** Implemented a global `window.fetch` interceptor in `lib/fetch.ts` loaded via `app/client-layout.tsx`. It caches identical in-flight GET requests and returns a cloned response to all subscribers.
**Hot path affected:** Any concurrent initial data fetches, navigation events, and repeated polling intervals across components on the frontend.
**Measurable improvement:** Reduced the number of outgoing concurrent network requests for the same URLs.
**Next opportunity:** An intelligent stale-while-revalidate caching mechanism with TTLs for non-volatile endpoints to allow immediate responses for already fetched data instead of only deduplicating strictly concurrent calls.
