## 2025-02-23 — Intent-based AI Pre-computation Engine
**Product understood as:** A Vishing and Smishing defense platform that analyzes SMS messages and calls to detect scams.
**Prediction invented:** Anticipates the user clicking "Analyze SMS" when they paste >15 characters and pause typing for 400ms. It fires the AI scan API request in the background.
**Data used:** User typing/pasting cadence (time delta between keystrokes in the SMS textarea).
**Impact:** Drops the perceived latency of the LLM-based scan from 2-3 seconds down to near 0ms, making the app feel instantaneously fast.
**Next opportunity:** Prefetching relevant dashboard statistics or predicting the user will report an SMS to cybercrime if the scan verdict is a high-confidence scam.
