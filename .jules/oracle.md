## 2024-06-19 — Predictive Threat Pre-Computation
**Product understood as:** An AI-powered defense system (VSDP) against vishing and smishing threats in India, heavily focused on detecting scams from SMS and phone calls in real-time.
**Prediction invented:** Behavioral Prefetching for the SMS scanner. If a user pastes or types a message (>15 chars) and pauses for 600ms, the app pre-computes the threat analysis API call in the background before they even click "Analyze".
**Data used:** Text input length and typing cadence (debounced pause of 600ms) indicating high intent to analyze.
**Impact:** Eliminates perceived AI inference latency. When the user clicks "Analyze", the network request and analysis are already done, dropping response time from ~2 seconds to near zero.
**Next opportunity:** Investigate predictive routing or caching for the dashboard summary based on user navigation habits (e.g. warming up dashboard data on login).
