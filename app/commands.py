"""Telegram-friendly commands for lead review."""

HELP = (
    "Business Agents commands:\n"
    "/start - start the assistant\n"
    "/help - show commands\n"
    "/lead Business | website | location | problem - create a lead preview\n"
    "/approve - approve the current proposed action\n"
    "/reject - reject the current proposed action"
)


def parse_lead_command(text: str) -> dict | None:
    prefix = "/lead"
    if not text.lower().startswith(prefix):
        return None
    parts = [p.strip() for p in text[len(prefix):].split("|")]
    if not parts or not parts[0]:
        return None
    return {
        "name": parts[0],
        "website": parts[1] if len(parts) > 1 and parts[1] else None,
        "location": parts[2] if len(parts) > 2 and parts[2] else None,
        "reason": parts[3] if len(parts) > 3 and parts[3] else None,
        "source": "telegram-owner-input",
    }
