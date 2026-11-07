## 2024-06-25 — Predictive SMS Scanning
**Product understood as:** VSDP is a platform for detecting and analyzing Vishing & Smishing threats. The SMS scanner is a key feature used to analyze suspicious texts.
**Prediction invented:** Predictive pre-computation of SMS AI analysis. Instead of waiting for users to paste text and then click "ANALYZE", the engine debounces user input by 500ms and pre-fetches the scan analysis in the background while the user decides to click the button.
**Data used:** User input text stream into the SMS text area.
**Impact:** When users finally click "ANALYZE SMS", the API response is already fetched (or in-flight), eliminating the perceived 400ms-2s API wait time and making the UI feel impossibly fast.
**Next opportunity:** Route pre-fetching when users hover over links or predictively warm up data for the threat dashboard.
