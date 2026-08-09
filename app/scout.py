"""Scout agent: turns public lead records into reviewable opportunities.

It never contacts a business. It only works from information supplied by an
approved public-data source or by the owner.
"""
from .lead_finder import prepare_lead


def scout(records: list[dict]) -> list[dict]:
    opportunities = []
    for record in records:
        lead = prepare_lead(**{
            "name": str(record.get("name", "")).strip(),
            "website": record.get("website"),
            "location": record.get("location"),
            "public_contact": record.get("public_contact"),
            "source": record.get("source"),
            "reason": record.get("reason"),
        })
        if lead["name"]:
            opportunities.append(lead)
    return opportunities
