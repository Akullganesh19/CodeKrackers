## 2024-11-20 — Intent-to-Analyze Prefetching
**Product understood as:** A cybersecurity tool to detect and mitigate voice and SMS-based fraud (Vishing and Smishing).
**Prediction invented:** Behavioral Pre-computation (Intent-to-Analyze Prefetching). I added a system that detects when a user stops typing into the SMS Scanner. If they pause for 600ms, the frontend silently triggers the backend BERT scan in the background. When the user actually clicks "ANALYZE", the cached result is shown instantly.
**Data used:** The user's interaction and pause duration with the text area in the SMS Scanner (`text` state mutations and debouncing).
**Impact:** 0ms perceived latency for users who type or paste SMS messages and then take a brief moment before clicking the "Analyze" button, completely bypassing the loading spinner and waiting on the backend.
**Next opportunity:** Next-Action Prediction for the Dashboard/Analytics view: prefetching detailed view of the highest-threat item since that's often the first thing an admin clicks.
