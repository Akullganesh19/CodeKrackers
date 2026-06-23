## 2024-06-23 — [Zero-Latency SMS Scan Prefetch]
**Product understood as:** A specialized anti-fraud/security app targeting SMS Smishing, voice scams, and threats, intended for citizens, banks, officers, and admins.
**Prediction invented:** Silent predictive prefetch of SMS scan analysis. When a user pastes or types a suspicious SMS into the text box, a background process debounces their input and silently initiates the network request to `http://localhost:8000/api/analytics/scan`. The Promise is stored in a React `useRef`.
**Data used:** The unsubmitted content of the `textarea` block where users input their suspicious SMS.
**Impact:** When users explicitly click "ANALYZE SMS", instead of waiting hundreds of milliseconds for a full network round trip and AI inference, the result resolves instantly from the cached prefetch, making the system feel impossibly fast. It gracefully degrades if the text changed last-minute or if the prefetch failed.
**Next opportunity:** Implement route prefetching in the sidebar so that frequently visited dashboard routes are pre-rendered before click.
