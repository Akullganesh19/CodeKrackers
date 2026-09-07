## 2024-05-14 — SMS Predictive Engine
**Product understood as:** VSDP is a cybersecurity platform focused on detecting voice and SMS threats, tracking real-time intel in India.
**Prediction invented:** Predictive Intelligence Engine (`lib/oracle.ts`) that debounces user input in the SMS scanner textarea and silently precomputes the `/api/analytics/scan` backend result while they are typing or pausing.
**Data used:** The textarea string contents of the SMS scanner page (`app/sms-scanner/page.tsx`).
**Impact:** Zero-latency perceived response time when users click "ANALYZE SMS" because the fetch result is cached as a cloned Promise and instantly retrieved.
**Next opportunity:** Prefetch threat details on hover in the Live Activity Dashboard.
