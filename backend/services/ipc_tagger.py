def tag_ipc_sections(threat_type: str, risk_factors: list) -> list[dict]:
    """
    Auto-tags relevant IPC (Indian Penal Code) and IT Act sections   # noqa: W291
    based on the detected threat type and risk factors.
    """
    sections = []

    # Always include for any cyber fraud detected by VSDP platform
    sections.append({
        "section": "IT Act 2000 §66D",
        "description": "Punishment for cheating by personation by using computer resource"  # noqa: E501
    })

    threat_type = threat_type.lower()
    risk_factors_str = " ".join([str(rf).lower() for rf in risk_factors])

    # Smishing, Vishing, and AI Voice Deepfakes involve identity manipulation
    if threat_type in ['smishing', 'vishing', 'ai_voice']:
        sections.append({
            "section": "IT Act 2000 §66C",
            "description": "Punishment for identity theft"
        })
        sections.append({
            "section": "IPC §420",
            "description": "Cheating and dishonestly inducing delivery of property"
        })

    # Financial frauds involving OTP or Banking details
    if "otp" in risk_factors_str or "bank" in risk_factors_str:
        sections.append({
            "section": "IPC §468",
            "description": "Forgery for purpose of cheating"
        })

    # Specific to AI Voice / Deepfakes
    if threat_type == 'ai_voice':
        sections.append({
            "section": "IT Act 2000 §66E",
            "description": "Punishment for violation of privacy"
        })
        sections.append({
            "section": "IPC §471",
            "description": "Using as genuine a forged document or electronic record"
        })

    # Impersonation of Public Servants (e.g., Police, TRAI, RBI)
    if "authority" in risk_factors_str or "police" in risk_factors_str or "officer" in risk_factors_str:  # noqa: E501
        sections.append({
            "section": "IPC §170",
            "description": "Personating a public servant"
        })

    # Deduplicate sections by section code
    unique_results = []
    seen = set()
    for item in sections:
        if item["section"] not in seen:
            unique_results.append(item)
            seen.add(item["section"])

    return unique_results  # noqa: W292
