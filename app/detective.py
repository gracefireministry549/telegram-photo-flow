"""Detective agent for evidence-based problem analysis."""


def investigate(lead: dict) -> dict:
    evidence = []
    if lead.get("website"):
        evidence.append({"type": "website", "value": lead["website"]})
    if lead.get("source"):
        evidence.append({"type": "source", "value": lead["source"]})
    reason = (lead.get("reason") or "").strip()

    return {
        "lead": lead,
        "evidence": evidence,
        "problem": reason or None,
        "confidence": "medium" if reason and len(evidence) >= 1 else "low",
        "needs_review": not bool(reason),
        "instruction": "Do not claim a problem as fact unless supported by evidence.",
    }
