## 2025-03-02 — Request Coalescing and Stale-While-Revalidate Caching
**Gap found:** The frontend components (like \`dashboard\`, \`analytics\`, \`sms-scanner\`) were making independent, un-cached \`fetch()\` calls to the same endpoints simultaneously, and re-fetching data on every render without local caching or deduplication.
**Why it existed:** Quick scaffolding meant each component managed its own networking, resulting in a thundering herd on the backend and felt latency for the user while waiting for identical network requests to resolve.
**Built:** Introduced \`dedupedFetch\` in \`app/lib/api.ts\`. It acts as an invisible network layer that:
1. Coalesces identical in-flight GET requests (so 5 components asking for the same data result in 1 network call).
2. Implements a Stale-While-Revalidate cache pattern. Hot data is returned instantly from the cache, while a background request silently updates the cache if the data is getting stale.
**Hot path affected:** Every authenticated dashboard and analytics page load.
**Measurable improvement:** Reduces redundant network calls to 1 per resource. Lowers perceived latency for cached resources to 0ms (instant UI render).
**Next opportunity:** Implement predictive pre-fetching based on cursor movement or implement an intelligent queue for heavy background writes.
