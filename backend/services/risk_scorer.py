class RiskScorer:
    """
    Engine to compute multi-factor risk scores by combining ML model outputs
    with heuristic risk signals.
    """

    def compute_sms_risk(
        self,
        model_confidence: float,
        risk_factors: list,
        has_suspicious_url: bool,
        sender_in_blacklist: bool,
    ) -> dict:
        """
        Computes risk for Smishing threats using a weighted formula.
        Score range: 0.0 to 1.0
        """
        # Weighted components
        base_score = model_confidence * 0.5
        url_score = 0.25 if has_suspicious_url else 0
        factor_score = min(len(risk_factors) * 0.05, 0.15)
        blacklist_score = 0.10 if sender_in_blacklist else 0

        final_score = min(base_score + url_score + factor_score + blacklist_score, 1.0)
        severity = self._get_severity(final_score)

        return {"risk_score": round(final_score, 4), "severity": severity}

    def compute_voice_risk(
        self,
        model_confidence: float,
        deepfake_score: float,
        flagged_phrases_count: int,
        caller_spoofed: bool,
    ) -> dict:
        """
        Computes risk for Vishing or AI Voice threats using a weighted formula.
        Score range: 0.0 to 1.0
        """
        # Weighted components
        base_score = model_confidence * 0.4
        deep_score = deepfake_score * 0.3
        phrase_score = min(flagged_phrases_count * 0.06, 0.2)
        spoof_score = 0.10 if caller_spoofed else 0

        final_score = min(base_score + deep_score + phrase_score + spoof_score, 1.0)
        severity = self._get_severity(final_score)

        return {"risk_score": round(final_score, 4), "severity": severity}

    def _get_severity(self, score: float) -> str:
        """
        Maps a numerical risk score to a human-readable severity level.
        """
        if score < 0.3:
            return "low"
        elif score < 0.6:
            return "medium"
        elif score < 0.8:
            return "high"
        else:
            return "critical"
