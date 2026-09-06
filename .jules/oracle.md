## 2024-03-24 — Predictive SMS Analysis

**Product understood as:** VSDP is a vishing and smishing defense platform that analyzes SMS texts and call transcripts for threats.

**Prediction invented:** Predictive pre-computation of SMS threat analysis. When the user pastes or types an SMS into the scanner textarea, we predict they will click "ANALYZE SMS". We use a debounced background predictive fetch to pre-compute the analysis result before they even click the button.

**Data used:** The textarea `onChange` event (keystrokes / paste) and the resulting `text` state.

**Impact:** Near-zero latency perceived by the user when they click "ANALYZE SMS" because the result has already been fetched and cached.

**Next opportunity:** Route prefetching in the sidebar or predictive fetching for dashboard summary stats on hover.
