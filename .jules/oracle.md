## 2024-07-04 — [Predictive Pre-computation & Route Prefetching]
**Product understood as:** Vishing and Smishing Defense Platform (VSDP), an app for tracking, analyzing, and mitigating SMS and voice threats in India. Users act on threat feeds and actively use the AI text scanner.
**Prediction invented:** Implemented a two-pronged predictive engine:
1. **Behavioral Pre-computation:** Analyzes user typing cadence in the SMS Scanner. If the text string is long enough, the Oracle pre-computes the ML inference call in the background before the user clicks "Analyze SMS".
2. **Route Prefetching:** Observes mouse hover events over the sidebar navigation. When a user moves towards a route (e.g., Dashboard or Analytics), the Oracle anticipates the data needed for that view and begins fetching the API payloads (like `dashboard-summary` or `threat_map`) before the navigation occurs.
**Data used:** User input text length (debounced) and Sidebar mouse hover signals.
**Impact:**
1. The perceived latency of the SMS AI Scan drops to near-zero (~50ms cache retrieval vs. 800ms+ ML inference time) because the answer is ready the moment they hit the button.
2. Dashboard and Analytics pages render their initial charts instantly instead of displaying loading spinners while waiting for API calls to resolve.
**Next opportunity:** Pre-fill threat report forms based on the last detected threat, predicting that users will want to report the very thing they just analyzed.
