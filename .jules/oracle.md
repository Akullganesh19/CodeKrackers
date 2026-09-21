## 2024-05-28 — [Predictive SMS Analysis]
**Product understood as:** Cybersecurity platform for scanning SMS for smishing (phishing via SMS).
**Prediction invented:** Anticipating the user's need to analyze the SMS. As the user pastes or types a sufficiently long message in the SMS scanner textarea, Oracle will preemptively send it to the backend for analysis in the background before they even click "ANALYZE SMS".
**Data used:** The textarea input value.
**Impact:** When the user clicks the "ANALYZE SMS" button, the result will appear almost instantaneously (zero-latency) because it was already precomputed while they were reading or moving their mouse to the button.
**Next opportunity:** Pre-fetching known threat patterns/recent detections when the dashboard loads.
