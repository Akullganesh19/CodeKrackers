## 2024-05-19 — Predictive SMS Scan Prefetching
**Product understood as:** An intelligence dashboard and threat analysis tool. The SMS scanner accepts user input text, and when a button is clicked, an API performs a slow AI-based check to score risk.
**Prediction invented:** Implemented a predictive prefetch that anticipates the user's intent to scan. It uses a 400ms debounce on the textarea input to silently pre-trigger the API in the background while the user is still interacting with the page, storing the Promise in a component ref cache.
**Data used:** The user's input `text` inside the `app/sms-scanner/page.tsx` text box, captured during the typing sequence.
**Impact:** Eliminates perceived latency. By the time the user finishes typing or reviewing the text and clicks "Analyze," the background request has either completed or is already underway. To the user, a 1-second delay now feels instantaneous.
**Next opportunity:** Prefetch threat details pages by anticipating which log item the user will click on in the dashboard feed based on mouse movement towards a row, or hovering over threat IDs.
