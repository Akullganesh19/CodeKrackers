## 2024-07-07 — Predictive Route Pre-fetching and SMS Pre-computation
**Product understood as:** VSDP (Vishing & Smishing Defense Platform) command center where users detect threats via SMS text or Voice Audio.
**Prediction invented:**
  1. Background predictive prefetching of the `/api/analytics/dashboard-summary` and `/api/analytics/threat_map` routes triggered when the user's cursor hovers over the navigation links in the Sidebar.
  2. Background prediction of SMS scans; when the user stops typing in the SMS scan box for 800ms, the system preemptively sends an inference request so that by the time they hit the "Analyze" button, the scan result returns instantly.
**Data used:**
  1. Hover intent on navigation icons (`onMouseEnter`).
  2. Idle typing time within the input text box (`setTimeout` over `text` length changes).
**Impact:** Eliminates perceived backend latency for large API payloads and AI inference scans, creating a 'zero latency' experience for the highest-frequency actions.
**Next opportunity:** Predicting likely malicious phone numbers via pre-scanning the call logs when users upload audio in the Call Monitor.
