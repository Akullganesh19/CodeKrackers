## 2025-02-28 — Global Request Coalescing
**Gap found:** Multiple identical `fetch` calls to endpoints without duplication logic, resulting in unnecessary network traffic and thundering herds during rapid UI component mounts.
**Why it existed:** The app relied on plain React effect hooks or simple handlers for fetching data across multiple sibling components without a centralized HTTP client abstraction to deduplicate identical in-flight requests.
**Built:** `PhantomProvider`, a global `window.fetch` interceptor using a Next.js client component (`app/components/PhantomProvider.tsx`). It implements Request Coalescing using an `inFlight` Map to deduplicate simultaneous GET requests, cleanly bypassing Next.js RSC router fetches to preserve framework compatibility.
**Hot path affected:** Every client-side `fetch` call across the app.
**Measurable improvement:** Multiple rapid component mounts fetching the same URL now coalesce to exactly 1 HTTP request across the network, reducing backend load and resolving race conditions.
**Next opportunity:** Background Sync queue to defer non-critical POST mutations or offline request queue.
