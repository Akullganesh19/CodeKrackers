## 2024-05-18 — Request Coalescing Fetch Wrapper
**Gap found:** Multiple components frequently made identical simultaneous GET requests to the same endpoints independently.
**Why it existed:** Different UI components independently needed the same data (e.g. analytics stats, safety score) without a centralized state manager, leading to duplicate network hits on page load.
**Built:** Invisible request coalescing middleware that intercepts `window.fetch`. It holds in-flight GET request Promises in an in-memory Map, immediately returning a clone of the Response to any subsequent identical requests until the original completes.
**Hot path affected:** Client-side rendering across dashboards where independent widgets fetch overlapping data simultaneously.
**Measurable improvement:** Reduces duplicate network round trips, easing server load and improving client side rendering latency by avoiding redundant TCP/HTTP setup.
**Next opportunity:** Stale-while-revalidate caching mechanism to serve previous responses immediately while checking for updates.
