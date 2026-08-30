## 2024-05-18 — Predictive SMS Scan Precomputation
**Product understood as:** VSDP is a platform for citizens and admins to scan, monitor, and report fraudulent activities, notably smishing (SMS scams) and vishing (voice scams).
**Prediction invented:** An OracleEngine that pre-computes SMS threat analysis while the user is typing/pasting, rather than waiting for them to click "Analyze".
**Data used:** The `onChange` event of the text area in the SMS scanner page, which signals user intent before the final submission.
**Impact:** Eliminates the latency of the backend scan API call when the user clicks "Analyze" because the result is already fetched in the background. Perceived load time goes from ~1000ms+ to ~0ms.
**Next opportunity:** Pre-compute voice scan analysis when users select an audio recording or during live recording pauses.
