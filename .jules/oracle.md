## 2024-07-17 — Predictive SMS Pre-computation
**Product understood as:** An SMS Smishing Scanner that analyzes potentially malicious text messages using AI/BERT to protect users from scams.
**Prediction invented:** Implemented a predictive Oracle engine that debounces user typing and pre-computes the AI scan API response before the user clicks 'ANALYZE SMS'.
**Data used:** The keystrokes (`onChange` events) on the SMS text area input field.
**Impact:** Zero-latency UI. When the user finishes pasting or typing a suspicious SMS and clicks analyze, the result is instantaneous because the network request already resolved in the background.
**Next opportunity:** Pre-fetching dynamic dashboard statistics or risk severity levels when a user hovers over sidebar links, creating zero-latency dashboard navigation.
