## $(date +%Y-%m-%d) — Global Request Coalescing (In-flight Fetch Deduplication)

**Gap found:** Multiple components in the Next.js app were naively fetching the exact same API endpoints simultaneously on page loads and component mounts, leading to duplicate network requests for identical resources.
**Why it existed:** There was no centralized infrastructure to intercept and deduplicate in-flight requests, and React components often trigger isolated fetch calls when mounted independently.
**Built:** `PhantomProvider`, a global invisible wrapper around `window.fetch`. It intercepts outgoing `GET` requests, creates a cache key, and if a request is already in flight, it returns a clone of the original promise instead of initiating a new network call. It safely bypasses RSC, Next.js internal requests, and `no-store` requests.
**Hot path affected:** Every client-side API call throughout the frontend application, particularly heavy analytics and dashboard queries that may be requested by multiple UI components simultaneously.
**Measurable improvement:** Reduced redundant network requests on initial page loads and dense views (like `/dashboard` and `/analytics`). The backend receives fewer identical overlapping queries, freeing up connections and database resources.
**Next opportunity:** Implement a background sync or offline queue for write operations to make user actions feel instant regardless of network latency.
