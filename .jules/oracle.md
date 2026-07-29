## 2025-02-20 — Zero-Latency SMS Pre-computation
**Product understood as:** VSDP is a vishing and smishing defense platform where users paste or input suspect messages to receive threat intelligence scans.
**Prediction invented:** Anticipatory background scanning. When a user pauses typing for 500ms, the system initiates the backend `fetch` request predicting they will hit 'Analyze'.
**Data used:** The textarea `onChange` events and string length/debouncing.
**Impact:** Perceived latency drops dramatically; when the user finally clicks the analyze button, the scan results often resolve instantly from a locally cached `Promise`.
**Next opportunity:** Prefetching specific dashboard threat reports in the background when the user hovers over a row in the "Threat Flow" table on the Command Center.
