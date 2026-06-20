## 2024-06-20 — Predictive SMS Analysis Prefetching

**Product understood as:** An AI-powered cybersecurity platform for detecting vishing and smishing threats in India. Users include citizens reporting threats and officers investigating them.

**Prediction invented:** Predictive prefetching for SMS scam analysis. Instead of waiting for the user to explicitly click "ANALYZE SMS", the app detects when they pause typing (800ms hesitation after entering >15 characters) and silently pre-computes the threat analysis via a background fetch.

**Data used:** The user's real-time typing cadence in the SMS text area, specifically leveraging typing pauses as a signal of input completion or consideration.

**Impact:** The perceived latency of the complex BERT model analysis drops from several seconds to near-zero. If the user clicks "Analyze" after pausing, the UI instantly resolves using the cached Promise. If they change the text, it gracefully degrades to a standard fetch.

**Next opportunity:** Session Warm-up. On app load or login, proactively prefetch the user's dashboard summary and most recent unread threats before they navigate to those specific views.
