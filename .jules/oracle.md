## 2025-02-28 — Zero-Latency Behavioral Prefetching
**Product understood as:** VSDP (Vishing & Smishing Defense Platform) - A React/Next.js dashboard used by citizens and cybercrime officers to monitor and report scams.
**Prediction invented:** A global `window.fetch` interceptor (`OraclePredictor.tsx`) that anticipates user navigation. It detects when a user is on the root or login page and autonomously prefetches the high-latency `/api/analytics/dashboard-summary` endpoint before they click 'Sign In', holding the cloned HTTP response in a memory cache.
**Data used:** Current active route (`usePathname()`) from the Next.js router.
**Impact:** Dashboard loading time drops from ~1.5s down to 0ms (instantaneous) because the data is already waiting in memory when the dashboard finally mounts and requests it.
**Next opportunity:** Predicting which FIR a user will click next based on cursor trajectory and prefetching the PDF evidence.
