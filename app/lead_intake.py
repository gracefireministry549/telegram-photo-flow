"""Normalize lead research supplied by a public-data source or by the owner.

The module intentionally does not scrape private information or contact anyone.
It produces clean records for the approval pipeline.
"""

from typing import Iterable
from .lead_finder import prepare_lead


def normalize_leads(records: Iterable[dict]) -> list[dict]:
    """Validate and score a batch of lead records."""
    results = []
    for record in records:
        if not isinstance(record, dict):
            continue
        name = str(record.get("name", "")).strip()
        if not name:
            continue
        clean = {
            "name": name,
            "website": record.get("website"),
            "location": record.get("location"),
            "public_contact": record.get("public_contact"),
            "source": record.get("source"),
            "reason": record.get("reason"),
        }
        results.append(prepare_lead(**clean))
    return results
