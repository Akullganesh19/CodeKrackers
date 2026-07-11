## 2025-02-12 — Predictive Scan Engine

**Product understood as:** A Vishing & Smishing Defense Platform that helps users scan suspicious text messages for malicious content and scam patterns.
**Prediction invented:** Implemented a `preComputeScan` engine that predicts when a user is likely to analyze an SMS. By tracking the `onChange` event of the input textarea and debouncing the input, the engine silently fires off a request to the backend scanner in the background before the user even clicks the "Analyze" button.
**Data used:** The textarea input string length and activity (debounced `onChange` typing/pasting signal).
**Impact:** When the user finally clicks the "Analyze" button, the results return almost instantly (zero perceived latency) because the HTTP request was already completed or is already underway.
**Next opportunity:** Expand background precomputation to other heavy user actions, like uploading an audio file for call monitoring, or prefetching dashboard metrics when a user logs in.
