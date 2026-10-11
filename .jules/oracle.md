## 2024-05-18 — Predictive SMS Analysis
**Product understood as:** VSDP is a vishing & smishing defense command center for analyzing cybersecurity threats.
**Prediction invented:** Predictive Fetch for SMS Scanning. While a user is typing/pasting an SMS message into the scanner and pauses for 500ms, the frontend quietly fires the `/api/analytics/scan` POST request in the background and caches the `Response`.
**Data used:** The current length and content of the user's input in the textarea.
**Impact:** When the user finally clicks the "ANALYZE SMS →" button, the results are near-instantaneous (~50ms perceived latency vs ~2-4s for an LLM analysis), making the threat detection feel impossibly fast.
**Next opportunity:** Predicting navigation routes based on the current active threat in the command center.
