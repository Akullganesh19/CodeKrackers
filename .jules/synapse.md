## 2024-06-25 — User Vulnerability Enrichment
**Systems connected:** [Auth/Users ↔ Spam Shield]
**Intelligence emerged:** [The spam filter is now dynamically more protective for users with a low safety score. Vulnerable users get a penalty added to their spam score automatically, without needing to manually configure their filter.]
**Data flows:** [User.safety_score is read by Spam Shield to enrich the threat evaluation and increase the score.]
**Coupling approach:** [Enrichment Pattern. Spam Shield fetches the User model during its normal database query flow to augment the calculation, without tightly coupling logic directly into the User module.]
**Next connection:** [Threat Detection ↔ Automated Notifications for spikes in attacks.]
