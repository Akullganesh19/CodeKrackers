## 2025-02-23 — Intelligent Request Coalescing & Caching

**Gap found:** Multiple components on the frontend were independently firing duplicate `fetch` requests for identical backend endpoints simultaneously (e.g., dashboard summaries, safety scores, threats maps). There was no application-level request batching or caching.
**Why it existed:** Quick scaffolding meant each component managed its own data fetching via `useEffect` without shared React contexts or global state.
**Built:** A central request orchestrator (`app/lib/api.ts`) exporting `dedupedFetch` that handles request coalescing (preventing in-flight duplicates) and stale-while-revalidate caching. Substituted raw `fetch` across major dashboards (`app/dashboard`, `app/analytics`, `app/sms-scanner`).
**Hot path affected:** Initial dashboard page loads, automatic polling intervals, and navigation between views heavily reliant on `/api/analytics/*` endpoints.
**Measurable improvement:** Reduces redundant backend hits per page load by strictly multiplexing simultaneous requests. Background caching ensures zero-perceived-latency renders for recently visited data.
**Next opportunity:** Implement persistent intelligent background syncing (e.g., using service workers or IndexedDB) for offline data mutations and optimistic UI updates for form submissions.
