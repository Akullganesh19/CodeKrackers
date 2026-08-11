## 2024-08-11 — SMS Scan Predictive Caching
**Product understood as:** Vishing & Smishing Defense Platform (VSDP), which analyzes SMS messages for malicious content via BERT model.
**Prediction invented:** Added a predictive caching system in `lib/oracle.ts` and updated `app/sms-scanner/page.tsx` to pre-compute the SMS scan while the user is typing (using a 500ms debounce), achieving zero-latency when the user clicks 'Analyze'.
**Data used:** The textarea's `onChange` event provides the text for early API requests.
**Impact:** Users will experience instantaneous feedback when clicking 'Analyze' if they typed the text and waited at least 500ms plus the API round trip, hiding the network latency in the background.
**Next opportunity:** Prefetch threat details on hover in the recent detections list in the dashboard to make clicking on a threat feel instant.
