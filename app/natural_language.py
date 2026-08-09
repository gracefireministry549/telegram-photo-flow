"""Simple natural-language command understanding with no extra AI API."""
import re


def understand(text: str) -> dict:
    t = text.strip().lower()
    if not t:
        return {"intent": "empty", "reply": "Tell me what you want me to do."}

    if any(x in t for x in ("find clients", "find leads", "find businesses", "look for clients", "get me clients")):
        return {"intent": "find_leads", "topic": text.strip()}
    if any(x in t for x in ("approve", "go ahead", "do it")):
        return {"intent": "approve"}
    if any(x in t for x in ("reject", "don't do it", "do not do it", "cancel")):
        return {"intent": "reject"}
    if any(x in t for x in ("help", "what can you do", "what do you do")):
        return {"intent": "help"}
    if any(x in t for x in ("status", "what have you done", "progress")):
        return {"intent": "status"}
    return {"intent": "general", "topic": text.strip()}
