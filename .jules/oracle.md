## 2025-05-15 — Predictive SMS Scanning
**Product understood as:** VSDP is a vishing and smishing defense platform where users paste suspicious SMS texts or monitor calls to check for scams.
**Prediction invented:** Implemented a predictive intelligence module (`app/lib/oracle.ts`) that initiates a background scan API fetch while the user is typing/pasting an SMS.
**Data used:** The text in the `<textarea>` input on the SMS Scanner page (`app/sms-scanner/page.tsx`).
**Impact:** When users finish typing/pasting and click "ANALYZE SMS", the result appears instantly (zero latency) because the network request was already fired in the background and the promise cached.
**Next opportunity:** Predicting navigation flows (e.g., prefetching dashboard statistics when a user logs in).
