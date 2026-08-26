## 2025-05-18 — Behavioral Prefetch for AI Scanning
**Product understood as:** A Vishing & Smishing Defense Platform (VSDP) that analyzes text and audio for fraud.
**Prediction invented:** An Oracle prediction engine (`lib/oracle.ts`) that silently prefetches AI scan results while the user is typing/pasting a suspicious SMS.
**Data used:** Keyboard typing behavior (debounced text input from the SMS scanner textarea).
**Impact:** When the user finishes typing or pasting an SMS and clicks "Analyze SMS", the network request has often already completed in the background, resulting in zero perceived latency instead of waiting for the LLM/BERT backend.
**Next opportunity:** Route prefetching on the dashboard (predicting which details a user will view based on severity) or predicting the next action (like automatically generating an FIR draft in the background if a scan returns critical severity).
