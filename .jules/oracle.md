## 2025-01-20 — Predictive SMS Scan Background Computation
**Product understood as:** VSDP is a platform for detecting and analyzing Vishing and Smishing scams. Users can paste suspicious SMS messages to analyze them.
**Prediction invented:** Predictive Intelligence module (Oracle) to background pre-compute SMS scan results. As the user types or pastes text in the scanner, we debounce and prefetch the BERT analysis from the backend before they click "ANALYZE SMS".
**Data used:** The textarea content (sms text). By caching unresolved Fetch promises, we avoid duplication when the user actually hits "ANALYZE".
**Impact:** Eliminates perceived latency (which was typically 300ms+ for BERT processing). By the time the user clicks analyze, the result is often already fetched or inflight, making the app feel impossibly fast.
**Next opportunity:** Prefetching analytics charts data before navigating to the analytics page, or warming up honeypot data on dashboard load.
