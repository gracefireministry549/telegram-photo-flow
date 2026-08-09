"""Problem-to-solution planning without claiming unverified facts."""


def propose_solution(lead: dict) -> dict:
    reason = (lead.get("reason") or "").strip()
    if not reason:
        return {
            "ready": False,
            "solution": None,
            "note": "More verified problem evidence is required before proposing a client solution.",
        }

    return {
        "ready": True,
        "solution": (
            "Review the verified problem, define a small measurable deliverable, "
            "prepare a personalized proposal, and wait for owner approval before outreach."
        ),
        "note": "This is a planning recommendation, not a claim that the business definitely has the problem.",
    }
