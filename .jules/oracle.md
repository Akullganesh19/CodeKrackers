## 2025-06-29 — Predictive Pre-computation for Threat Scanning

**Product understood as:** An AI-powered Vishing and Smishing Defense Platform for the Indian landscape, focused on detecting threats, logging evidence, and generating legal documentation (FIRs).
**Prediction invented:** Behavioral Prefetching (Pre-computation). Detects when a user has paused typing a suspicious SMS or voice transcript (500ms debounce) and proactively triggers the AI threat analysis in the background before they even click "Analyze".
**Data used:** Form field text (user input patterns in `text` and `manualText` states).
**Impact:** Eliminates perceived latency. By the time a user clicks the "Analyze" button, the backend LLM inference is either already complete or significantly underway, resulting in a near-instant UX instead of a multi-second wait.
**Next opportunity:** Session Warm-up / Route Prediction. We could pre-fetch dashboard analytics and heatmaps immediately upon login, or predict that a user will navigate to the `FIR Management` page after a `SCAM` detection.
