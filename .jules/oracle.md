## 2024-07-14 — Predictive SMS Pre-computation
**Product understood as:** VSDP is a cybersecurity platform designed to detect vishing and smishing threats in real-time. The SMS scanner is a key tool where users input text and wait for a BERT model analysis.
**Prediction invented:** Predictive SMS Pre-computation, where the AI scan begins in the background the moment a user finishes typing or pasting, effectively reducing the perceived wait time for inference to near zero.
**Data used:** The explicit but un-submitted text input stream from the user in the SMS scanner `textarea` via debounced `onChange` events.
**Impact:** Eliminates the typical 300-500ms network and inference latency when the user eventually clicks "ANALYZE SMS". The data is often already loading or resolved by the time they click.
**Next opportunity:** Expand prediction to the voice monitor—e.g., pre-fetch historical threat intelligence based on the caller ID the moment a call begins ringing, before the user even answers.
