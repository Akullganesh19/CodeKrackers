## 2024-11-20 — Predictive SMS Scan Pre-computation
**Product understood as:** VSDP (Vishing & Smishing Defense Platform) detects scam messages and calls.
**Prediction invented:** Implemented a predictive pre-computation cache in `app/lib/oracle.ts`. It anticipates user intent by pre-fetching analysis for SMS text continuously as they type (with a 500ms debounce) or load samples, instead of waiting for the user to explicitly press "Analyze SMS".
**Data used:** The user's input stream in the SMS Scanner text box and "Load Sample" buttons.
**Impact:** 0ms perceived latency for users after they finish typing or after clicking "Load Sample" and then "Analyze". Analysis is already ready by the time they request it.
**Next opportunity:** Prefetching reports/intelligence feeds on the dashboard while the user scrolls or when a new threat alert is generated.
