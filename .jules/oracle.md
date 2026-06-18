## 2024-06-18 — Initialize Oracle Journal

**Product understood as:** VSDP is a vishing and smishing defense platform for the Indian landscape, employing live scanning, call monitoring, honeypots, and a dashboard for cyber-crime prevention and auto-FIR generation.
**Initial thoughts:** Users likely check the dashboard frequently. Prefetching data on hover before clicking links (e.g., in the sidebar or main page) could vastly improve perceived latency. Background pre-computation for the analytics page (which polls every 30s) could be useful.

## 2024-06-18 — Predictive Data Engine

**Product understood as:** VSDP is a vishing and smishing defense platform for the Indian landscape.
**Prediction invented:** Implemented a global `PredictiveEngine` that anticipates user navigation. It includes Session Warm-up/Next-Action Prediction (prefetching `/dashboard` data when landing on `/` or `/login`) and Hover Intent Prediction (prefetching endpoint data defined in a route map when users mouse over internal links).
**Data used:** Route matching heuristics (users arriving at `/` typically navigate to `/dashboard` next) and explicit browser DOM `mouseover` events tracking cursor position relative to navigation links (`<a>`).
**Impact:** Loading perceived latency drops to near-zero as API data is often fully retrieved and cached before the React component even begins to mount.
**Next opportunity:** We could store individual user navigation sequences locally (e.g., this specific user *always* goes from `/dashboard` to `/dashboard/investigation`) to create highly personalized prefetching maps, or pre-compute common dashboard query filters server-side before request.
