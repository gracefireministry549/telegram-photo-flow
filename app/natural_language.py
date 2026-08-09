"""Plain-English intent detection for Telegram messages."""


def understand(text: str) -> dict:
    t = " ".join(text.strip().lower().split())
    if not t:
        return {"intent": "empty", "reply": "Tell me what you want me to do."}

    # Lead/client discovery. Handle singular and plural wording and common typos.
    lead_phrases = (
        "find client", "find clients", "find lead", "find leads",
        "find business", "find businesses", "look for client", "look for clients",
        "look for lead", "look for leads", "get me client", "get me clients",
        "get me lead", "get me leads", "get me business", "get me businesses",
        "search for client", "search for clients", "search for business",
        "search for businesses", "potential client", "potential clients",
    )
    if any(p in t for p in lead_phrases):
        topic = text.strip()
        return {"intent": "find_leads", "topic": topic}

    if any(x in t for x in ("approve", "go ahead", "do it")):
        return {"intent": "approve"}
    if any(x in t for x in ("reject", "don't do it", "do not do it", "cancel")):
        return {"intent": "reject"}
    if any(x in t for x in ("help", "what can you do", "what do you do")):
        return {"intent": "help"}
    if any(x in t for x in ("status", "what have you done", "progress")):
        return {"intent": "status"}

    return {"intent": "general", "topic": text.strip()}
