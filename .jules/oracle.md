## 2025-07-06 — [Predictive SMS Scanning]
**Product understood as:** A cybersecurity platform to detect voice and SMS fraud. The core user flow in the SMS scanner involves pasting a suspicious text message, waiting, and clicking analyze.
**Prediction invented:** Implemented a debounced background predictive pre-fetch (`preComputeScan`) that triggers as soon as the user finishes pasting or typing a suspicious SMS (over 10 chars). By the time they click "Analyze", the result is already computed and stored in a short-lived cache.
**Data used:** The length and content of the user's input in the textarea on the SMS scanner page, combined with a 500ms inactivity debounce.
**Impact:** Eliminates the ~300-800ms API inference latency. When the user clicks analyze, the result loads instantly from the cache, making the application feel impossibly fast.
**Next opportunity:** Predicting navigation paths (e.g. pre-fetching dashboard stats when hovering over the dashboard nav item).
