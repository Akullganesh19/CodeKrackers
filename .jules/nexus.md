## 2026-08-08 — Personal Security Score (Gamification)
**Product understood as:** VSDP is a cybersecurity platform handling threat reports and scam detections, currently aggregating stats across all users.
**Derivation reasoning:** We have an explicit `safety_score` field in the `users` table and a `score_history` table meant to track this score over time. We also track the `scams_avoided` on the `User` model. The backend `tasks.py` references daily updates to these scores. However, there is no endpoint for a user to see their personal security stats, nor a way for them to track how well they are protecting themselves. Gamifying security makes it much more likely they engage with the platform.
**Feature built:** Added a `/api/users/me/safety-score` endpoint and a 'My Safety Score' widget on the dashboard that shows the user's score, scams avoided, and protection status.
**User impact:** Users can now see a personal, gamified metric of their cyber hygiene, encouraging them to report more threats and be safer.
**Next logical feature:** User threat reporting leaderboard or gamified achievements (e.g. "Scam Buster Level 1").
