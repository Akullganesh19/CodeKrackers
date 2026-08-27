## 2026-08-27 — SMS Scanner Pre-computation
**Product understood as:** A threat detection and intelligence platform that processes SMS and voices using a hybrid AI backend to classify smishing and vishing attacks. Users paste text to analyze it.
**Prediction invented:** An Oracle caching layer that intercepts the "Analyze" action by starting the backend scan fetch request implicitly in the background (with a debounce) while the user is still typing/pasting text into the text area.
**Data used:** Form field input patterns. By listening to the `text` state in the SMS input box, we can trigger the backend request early.
**Impact:** 1-2 seconds of perceived latency are shaved off the "Analyze" button click because the AI inference has already started or completed in the background by the time the user explicitly submits it.
**Next opportunity:** Prefetch threat analytics summary endpoints on hover over the "Dashboard" link in the Sidebar, or pre-warm the "Vishing/Voice" scanner when an audio file upload starts.
