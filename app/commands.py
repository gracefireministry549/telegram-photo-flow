"""Telegram commands and simple natural-language intent parsing."""
import re

HELP = (
    "Business Agents understands normal English.\n\n"
    "Examples:\n"
    "• Find businesses in Lagos that need websites\n"
    "• Find me clients for social media marketing\n"
    "• Research this business and tell me how I can help\n"
    "• What should I do about this lead?\n\n"
    "Slash commands are optional."
)


def parse_lead_command(text: str) -> dict | None:
    prefix = "/lead"
    if not text.lower().startswith(prefix):
        return None
    parts = [p.strip() for p in text[len(prefix):].split("|")]
    if not parts or not parts[0]:
        return None
    return {"name": parts[0], "website": parts[1] if len(parts) > 1 and parts[1] else None,
            "location": parts[2] if len(parts) > 2 and parts[2] else None,
            "reason": parts[3] if len(parts) > 3 and parts[3] else None,
            "source": "telegram-owner-input"}


def parse_natural_language(text: str) -> dict | None:
    """Recognize common English requests without requiring a slash command."""
    original = text.strip()
    low = original.lower()
    if not original or low.startswith("/"):
        return None

    location = None
    for place in ["lagos", "abuja", "port harcourt", "ibadan", "enugu", "benin city", "kano", "nigeria", "london", "new york", "accra", "ghana"]:
        if re.search(rf"\b{re.escape(place)}\b", low):
            location = place.title()
            break

    service = None
    service_patterns = {
        "website": ["website", "web site", "websites", "web design"],
        "social media marketing": ["social media", "social media marketing"],
        "digital marketing": ["digital marketing", "online marketing"],
        "graphic design": ["graphic design", "flyer", "logo design"],
        "video editing": ["video editing", "video editor"],
        "seo": ["seo", "search engine optimization"],
    }
    for name, patterns in service_patterns.items():
        if any(p in low for p in patterns):
            service = name
            break

    asks_for_leads = any(w in low for w in ["find", "search", "look for", "get me", "give me", "discover"]) and any(w in low for w in ["business", "businesses", "clients", "leads", "companies", "customers"])
    asks_to_research = any(w in low for w in ["research", "analyze", "analyse", "check this business", "look at this business"])
    if not (asks_for_leads or asks_to_research):
        return None

    website_match = re.search(r"https?://\S+", original)
    website = website_match.group(0).rstrip(".,)") if website_match else None
    reason = original if not service else f"Potential need for {service}. Original request: {original}"
    return {
        "name": "Lead search" if asks_for_leads else "Business research",
        "website": website,
        "location": location,
        "reason": reason,
        "service": service,
        "task_type": "lead_search" if asks_for_leads else "research",
        "source": "telegram-natural-language",
    }
