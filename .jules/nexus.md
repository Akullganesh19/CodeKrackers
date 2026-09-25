## 2025-02-25 — Safety Score Gamification Dashboard

**Product understood as:** A comprehensive vishing and smishing defense platform that monitors communications, detects threats using AI, files automated FIRs, and tracks user proactive security involvement.

**Derivation reasoning:** The database tracks user behavior continuously and explicitly manages a `safety_score` field in the `User` model, which is incrementally adjusted based on actions like reporting scams or interacting with honeypots. The backend also runs tasks to snapshot this data into `ScoreHistory`. However, these gamification points and history are purely internal and completely unexposed to the user. Users logically need a way to see their safety score and track how their proactive defense efforts are benefiting their standing and the community.

**Feature built:**
- A new endpoint `GET /me/score-history` in `backend/api/users.py` to fetch a user's chronological score progression.
- A frontend component `app/safety-score/page.tsx` that visualizes the current score, daily trend, how points are earned or penalized, and a `recharts` graph of their score history.
- Added "Safety Score" to the `Sidebar` for discovery.

**User impact:** Users can now actively track their cybersecurity hygiene, creating a gamified loop that encourages better practices, active scam reporting, and honeypot interaction.

**Next logical feature:** Expose a Global Leaderboard of top proactive defenders (based on safety scores and honeypot intercepts) to create community competition and drive collective defense.
