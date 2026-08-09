"""Lead-finding foundation.

This module does not scrape private data or send outreach. It normalizes
publicly supplied/search results into a consistent lead record and applies
basic quality checks before a lead can enter the approval queue.
"""
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class Lead:
    name: str
    website: Optional[str] = None
    location: Optional[str] = None
    public_contact: Optional[str] = None
    source: Optional[str] = None
    reason: Optional[str] = None
    score: int = 0
    status: str = "new"

    def to_dict(self):
        return asdict(self)


def score_lead(lead: Lead) -> int:
    """Return a simple 0-10 fit score from verified fields.

    This is intentionally conservative: missing evidence lowers the score.
    """
    score = 0
    if lead.name.strip():
        score += 2
    if lead.website:
        score += 2
    if lead.location:
        score += 1
    if lead.public_contact:
        score += 2
    if lead.reason and len(lead.reason.strip()) >= 20:
        score += 3
    return min(score, 10)


def prepare_lead(**kwargs) -> dict:
    lead = Lead(**kwargs)
    lead.score = score_lead(lead)
    lead.status = "qualified" if lead.score >= 6 else "needs_review"
    return lead.to_dict()
