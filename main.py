"""Business Agents API and Telegram webhook."""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from app.pipeline import build_approval_queue
from app.approval import validate_action
from app.telegram import extract_message, extract_photo, send_message, register_webhook, answer_callback
from app.commands import HELP, parse_lead_command
from app.detective import investigate
from app.scout import scout
from app.solution import propose_solution
from app.approval_store import save_pending, decide
from app.telegram_ui import approval_keyboard
from app.natural_language import understand

@asynccontextmanager
async def lifespan(app: FastAPI):
    webhook_url = os.getenv("TELEGRAM_WEBHOOK_URL")
    if webhook_url and os.getenv("TELEGRAM_BOT_TOKEN"):
        await register_webhook(webhook_url)
    yield

app = FastAPI(title="Business Agents")
DASHBOARD = """<!doctype html><html><head><meta name='viewport' content='width=device-width,initial-scale=1'><title>Business Agents</title></head><body><main><h1>🤖 Business Agents</h1><p>AI-assisted business lead and problem-solving control center.</p><h2>Workflow</h2><p>Lead → Problem evidence → Solution → <b>YOU APPROVE</b> → Client → Job → Completion → Report</p><p>🟢 API online</p><p>Telegram: natural English enabled.</p></main></body></html>"""

class LeadRequest(BaseModel):
    name: str = Field(min_length=1)
    website: str | None = None
    location: str | None = None
    public_contact: str | None = None
    source: str | None = None
    reason: str | None = None

class ActionRequest(BaseModel):
    action: str

@app.get("/", response_class=HTMLResponse)
def dashboard(): return DASHBOARD

@app.get("/health")
def health(): return {"status": "ok", "service": "business-agents", "natural_language": True}

@app.post("/leads/preview")
def preview_lead(lead: LeadRequest): return build_approval_queue([lead.model_dump()])[0]

@app.post("/approval/validate")
def validate_approval(request: ActionRequest):
    action = validate_action(request.action)
    return {"action": action, "approved": action == "approve"}

@app.post("/telegram/webhook")
async def telegram_webhook(request: Request):
    update = await request.json()
    callback = update.get("callback_query")
    if isinstance(callback, dict):
        callback_id = callback.get("id")
        data = str(callback.get("data", ""))
        if ":" in data:
            action, key = data.split(":", 1)
            if action in {"approve", "reject", "edit"}:
                result = decide(key, action)
                if callback_id: await answer_callback(callback_id, f"{action.upper()} recorded")
                chat_id = ((callback.get("message") or {}).get("chat") or {}).get("id")
                if chat_id is not None:
                    await send_message(chat_id, f"✅ Decision recorded: {action.upper()}\nBusiness: {result.get('lead', {}).get('name', 'Unknown')}")
                return {"ok": True, "handled": True, "type": "callback", "action": action}

    message = extract_message(update)
    if not message: return {"ok": True, "handled": False}
    chat_id = message.get("chat", {}).get("id")
    photo = extract_photo(update)
    if photo and chat_id is not None:
        await send_message(chat_id, "📷 Photo received. Tell me in plain English what you want me to do with it.")
        return {"ok": True, "handled": True, "type": "photo", "file_id": photo.get("file_id")}

    text = (message.get("text") or "").strip()
    if chat_id is None: return {"ok": True, "handled": True}
    if text in ("/start", "/help"):
        await send_message(chat_id, "🤖 Business Agents ready. You can now talk to me in normal English.\n\n" + HELP)
        return {"ok": True, "handled": True, "type": "command"}

    intent = understand(text)
    if intent["intent"] == "help":
        await send_message(chat_id, "🤖 Just tell me what you need in normal English. For example: 'Find me businesses in Lagos that need websites.'")
        return {"ok": True, "handled": True, "type": "natural_language"}
    if intent["intent"] == "status":
        await send_message(chat_id, "📊 System is online. Telegram, lead scoring, solution planning and approval controls are active.")
        return {"ok": True, "handled": True, "type": "natural_language"}
    if intent["intent"] in {"approve", "reject"}:
        await send_message(chat_id, "I can apply that decision to a specific pending opportunity. Please tap its APPROVE or REJECT button.")
        return {"ok": True, "handled": True, "type": "natural_language"}

    lead_record = parse_lead_command(text)
    if lead_record:
        lead = scout([lead_record])[0]
        investigation = investigate(lead)
        proposal = propose_solution(lead)
        key = save_pending(chat_id, lead, proposal)
        reply = f"🔎 NEW OPPORTUNITY\n\nBusiness: {lead['name']}\nScore: {lead.get('score', 0)}/10\nProblem: {investigation.get('problem') or 'No verified problem supplied'}\nConfidence: {investigation.get('confidence')}\nProposed solution: {proposal.get('solution') or 'Need more evidence'}\n\n⚠️ Nothing will be sent to the business without your approval."
        await send_message(chat_id, reply, approval_keyboard(key))
        return {"ok": True, "handled": True, "type": "lead", "lead": lead}

    if intent["intent"] == "find_leads":
        await send_message(chat_id, f"🔎 I understand. You want me to find leads about: {intent['topic']}\n\nFor this first version, I need the public lead source/data connected before I can claim I found real businesses. I won't invent leads.")
        return {"ok": True, "handled": True, "type": "find_leads"}

    await send_message(chat_id, "🤖 I understand normal English. Tell me what you want done, who it is for, and any useful details. I will ask for approval before external outreach.")
    return {"ok": True, "handled": True, "type": "natural_language"}
