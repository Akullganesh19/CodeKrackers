## 2025-02-20 — Predictive SMS Scanning Engine
**Product understood as:** A Vishing and Smishing defense platform that analyzes SMS text and voice logs for threats.
**Prediction invented:** Implemented a predictive pre-computation engine (`oracle.ts`) that initiates a background scan API fetch when the user pauses typing for 800ms, caching the result stream.
**Data used:** The `onChange` text content in the SMS Scanner textarea and a debounce timer.
**Impact:** Users feel near-zero latency when clicking "Analyze SMS" because the backend prediction is already fetched and ready in the cache.
**Next opportunity:** Pre-fetch threat analysis logs when hovering over recent detections in the dashboard.
