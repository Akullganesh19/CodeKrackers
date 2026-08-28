## 2024-10-24 — Predictive Text Scanning Engine
**Product understood as:** A Vishing & Smishing Defense Platform (VSDP) designed to detect, analyze, and mitigate voice and SMS-based fraud.
**Prediction invented:** A prediction engine (`oracle.ts`) that caches unresolved Promises for SMS scanning. As the user types their text into the text area, it proactively initiates the API request behind the scenes. When the user clicks "Analyze", it immediately resolves the cached result instead of starting a new network request.
**Data used:** The text typed in the SMS scanner text area, debounced by 500ms to avoid unnecessary requests while typing.
**Impact:** Zero-latency UI. By the time the user clicks "Analyze", the backend NLP (BERT) has likely already processed the request. Users experience near-instant analysis results without the typical latency of a backend inference call.
**Next opportunity:** Prefetching specific dashboard summary data before navigation when a user hovers over the sidebar links or predicting which filters users will apply in analytics.
