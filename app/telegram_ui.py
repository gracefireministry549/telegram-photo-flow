"""Telegram inline approval UI helpers."""


def approval_keyboard(key: str) -> dict:
    return {
        "inline_keyboard": [[
            {"text": "🟢 APPROVE", "callback_data": f"approve:{key}"},
            {"text": "🔴 REJECT", "callback_data": f"reject:{key}"},
        ], [
            {"text": "✏️ EDIT", "callback_data": f"edit:{key}"},
        ]]
