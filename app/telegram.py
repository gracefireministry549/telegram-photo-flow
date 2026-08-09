"""Telegram webhook helpers."""
import os
from typing import Any
import httpx


def telegram_api_url(method: str) -> str:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not configured")
    return f"https://api.telegram.org/bot{token}/{method}"


def extract_message(update: dict[str, Any]) -> dict[str, Any] | None:
    message = update.get("message")
    return message if isinstance(message, dict) else None


def extract_photo(update: dict[str, Any]) -> dict[str, Any] | None:
    message = extract_message(update)
    if not message:
        return None
    photos = message.get("photo")
    if not isinstance(photos, list) or not photos:
        return None
    return photos[-1] if isinstance(photos[-1], dict) else None


async def send_message(chat_id: int | str, text: str, reply_markup: dict | None = None) -> dict:
    payload = {"chat_id": chat_id, "text": text}
    if reply_markup is not None:
        payload["reply_markup"] = reply_markup
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.post(telegram_api_url("sendMessage"), json=payload)
        response.raise_for_status()
        return response.json()


async def answer_callback(callback_query_id: str, text: str) -> dict:
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.post(
            telegram_api_url("answerCallbackQuery"),
            json={"callback_query_id": callback_query_id, "text": text},
        )
        response.raise_for_status()
        return response.json()


async def register_webhook(webhook_url: str) -> dict:
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.post(telegram_api_url("setWebhook"), json={"url": webhook_url})
        response.raise_for_status()
        return response.json()
