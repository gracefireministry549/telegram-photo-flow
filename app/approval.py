"""Human approval gate for external actions."""

ALLOWED = {"approve", "reject", "edit"}


def approval_message(lead: dict, solution: str) -> str:
    return (
        "NEW OPPORTUNITY\n\n"
        f"Business: {lead.get('name', 'Unknown')}\n"
        f"Score: {lead.get('score', 0)}/10\n"
        f"Problem evidence: {lead.get('reason') or 'Not yet established'}\n"
        f"Proposed solution: {solution}\n\n"
        "Action required: APPROVE, REJECT, or EDIT."
    )


def validate_action(action: str) -> str:
    action = action.strip().lower()
    if action not in ALLOWED:
        raise ValueError("Action must be approve, reject, or edit")
    return action
