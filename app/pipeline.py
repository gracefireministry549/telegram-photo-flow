"""Lead -> solution -> approval pipeline."""

from .lead_intake import normalize_leads
from .solution import propose_solution
from .approval import approval_message


def build_approval_queue(records: list[dict]) -> list[dict]:
    queue = []
    for lead in normalize_leads(records):
        proposal = propose_solution(lead)
        item = {
            "lead": lead,
            "proposal": proposal,
            "requires_owner_approval": True,
        }
        if proposal["ready"]:
            item["approval_message"] = approval_message(lead, proposal["solution"])
        queue.append(item)
    return queue
