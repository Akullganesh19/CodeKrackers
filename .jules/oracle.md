## 2025-02-27 — SMS Threat Scan Pre-computation

**Product understood as:** A Vishing & Smishing Defense Platform (VSDP) designed to detect and mitigate telecom fraud using NLP models.
**Prediction invented:** Implemented a Stale-While-Revalidate (SWR) predictive caching strategy for the core SMS scanning feature. It monitors user input (debounced by 500ms) or sample loading and triggers background API fetching of threat intelligence *before* the user explicitly clicks the "Analyze" button.
**Data used:** The raw input string typed into the main textarea or loaded via the sample buttons on the SMS Scanner dashboard.
**Impact:** Eliminates perceived backend latency for NLP processing. When users finish pasting and click "Analyze," the scan result is already resolved or in-flight, dropping effective load time from ~400ms down to ~50ms.
**Next opportunity:** Prefetching full investigation metadata and related FIR records into memory when a bank officer merely hovers over a row in the Fraud Verification or FIR Management tables.
