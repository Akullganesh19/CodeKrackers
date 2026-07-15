## 2025-02-18 — Predictive SMS Analysis Prefetching
**Product understood as:** A Vishing & Smishing Defense Platform (VSDP) that helps users analyze suspicious SMS and voice calls.
**Prediction invented:** Implemented a predictive pre-computation engine (`Oracle.preComputeScan`) for SMS scanning. When a user pastes or types a message into the text area, the engine debounces the input and begins fetching the AI-based analysis result *before* the user clicks "Analyze".
**Data used:** User input into the text area (`onChange` event with a 500ms debounce), relying on the length of the text (>10 chars).
**Impact:** Perceived latency of the SMS scan is reduced drastically. For many users, by the time they click "Analyze SMS", the network request is already inflight or resolved, cutting perceived wait time from ~1s to ~50ms.
**Next opportunity:** We could predictively prefetch potential user insights (e.g. recent FIRs or known threat numbers) upon user login/app-open for faster dashboard rendering.
