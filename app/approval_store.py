"""Small in-memory approval store for the first deployment.

This is intentionally simple. A persistent database can replace it later.
"""
from typing import Any

_PENDING: dict[str, dict[str, Any]] = {}


def save_pending(chat_id: int | str, lead: dict, proposal: dict) -> str:
    key = f"{chat_id}:{lead.get('name', 'lead')}"
    _PENDING[key] = {"lead": lead, "proposal": proposal, "status": "pending"}
    return key


def decide(key: str, action: str) -> dict[str, Any]:
    item = _PENDING.get(key)
    if not item:
        return {"found": False, "status": "not_found"}
    item["status"] = action
    return {"found": True, **item}
