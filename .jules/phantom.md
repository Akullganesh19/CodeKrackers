## 2024-05-15 — Request Coalescing Infrastructure
**Gap found:** The application lacked request coalescing, allowing multiple components on the same page to independently trigger simultaneous, identical API requests to the backend.
**Why it existed:** The app was built naively relying on Next.js/React standard `fetch` without an overarching client-side deduplication strategy to intercept and merge identical in-flight promises.
**Built:** A global `PhantomProvider` that hooks `window.fetch` to intercept and deduplicate identical, simultaneous `GET` requests using an in-flight Promise map, safely avoiding cache interference with `no-store` headers and React Server Components/Routing.
**Hot path affected:** Every client-side component performing concurrent data fetching on page loads or navigation events.
**Measurable improvement:** Redundant API requests to the backend on identical endpoints will be deduplicated, significantly reducing backend load and UI perceived latency during heavy simultaneous renders.
**Next opportunity:** Stale-while-revalidate caching implementation for the deduplicated fetch layer or predictive request caching based on cursor position/user intent.
