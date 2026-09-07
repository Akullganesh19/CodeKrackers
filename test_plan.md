**Product understood as:** VSDP is a cybersecurity platform focused on detecting voice and SMS threats, tracking real-time intel in India.
**Primary user flows:** Scanning suspicious SMS text (`/sms-scanner`), monitoring dashboard analytics (`/dashboard`), call monitoring.
**Data that exists:** User inputs SMS text into a textarea and then clicks "ANALYZE SMS".
**Prediction Opportunity:** The user is typing or pasting an SMS into the scanner textarea. We can precompute the `/api/analytics/scan` backend result while they are typing or pausing, instead of waiting for them to click "ANALYZE SMS".

I will invent a **Predictive Intelligence Engine** (`lib/oracle.ts`) that will:
1. Observe the user's typing in the SMS scanner (`app/sms-scanner/page.tsx`).
2. Debounce their input and silently trigger a background fetch to `/api/analytics/scan`.
3. Cache the Promise.
4. When the user eventually clicks "ANALYZE SMS", we immediately retrieve the pre-computed, cloned Promise instead of starting a new 300-800ms network round-trip.

This makes the app feel "impossibly ahead" with zero-latency responses for the main user action (scanning text).

### Execution Plan:
1. `bash`: Create `lib/oracle.ts` with the predictive engine logic (`preComputeScan` and `getScanResult`). (Done interactively).
2. `replace_with_git_merge_diff`: Inject the Oracle hooks into `app/sms-scanner/page.tsx`.
   - On `onChange`, invoke `preComputeScan`.
   - On `handleAnalyze`, check `getScanResult(text)` before triggering a new fetch.
3. Complete pre-commit steps to ensure proper testing, verification, review, and reflection are done.
4. `bash`: Update Oracle journal `.jules/oracle.md` using the exact format.
5. `submit`: Commit and push the branch.
