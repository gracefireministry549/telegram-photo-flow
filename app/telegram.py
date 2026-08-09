"""Telegram webhook helpers.

Secrets are read from environment variables at runtime. No bot token is
stored in this repository.
"""
import os
from typing import Any

import httpx


BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


def telegram_api_url(method: str) -> str:
    if not BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not configured")
    return f"https://api.telegram.org/bot{BOT_TOKEN}/{method}"


def extract_message(update: dict[str, Any]) -> dict[str, Any] | None:
    message = update.get("message")
    return message if isinstance(message, dict) else None


def extract_photo(update: dict[str, Any]) -> dict[str, Any] | None:
    """Return the largest Telegram photo size, if the update contains one."""
    message = extract_message(update)
    if not message:
        return None
    photos = message.get("photo")
    if not isinstance(photos, list) or not photos:
        return None
    return photos[-1] if isinstance(photos[-1], dict) else None


async def send_message(chat_id: int | str, text: str) -> dict:
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.post(
            telegram_api_url("sendMessage"),
            json={"chat_id": chat_id, "text": text},
        )
        response.raise_for_status()
        return response.json()
