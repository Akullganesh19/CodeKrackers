## 2024-05-08 — Threat Detection ↔ Blacklist Bridge (Auto-Blacklist)
**Systems connected:** Threat Detection (AI Scanning) ↔ Threat Intelligence (Community Blacklist)
**Intelligence emerged:** High-severity threats detected via automated voice/SMS scans (like AI Vishing/Smishing detection) instantly feed into the global blacklist system, protecting all other users proactively from that sender/caller instead of isolating the detection.
**Data flows:** Threat caller/sender IDs flow from `analytics.py` (AI scanning endpoints) and `threats.py` (Threat creation) into the `BlacklistEntry` model via the `auto_blacklist` function.
**Coupling approach:** Event-driven enrichment. The Threat system imports the loosely coupled `auto_blacklist` function and triggers it asynchronously (or synchronously but safely) after threat creation, without requiring the Blacklist system to know about the Threat system.
**Next connection:** Errors ↔ Users (Notify users when they encounter a known system bug).
