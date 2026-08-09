"""HTTP API for the business-agent approval workflow and Telegram webhook."""
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from app.pipeline import build_approval_queue
from app.approval import validate_action
from app.telegram import extract_message, extract_photo, send_message

app = FastAPI(title="Business Agents")


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
def dashboard():
    with open("app/dashboard.html", "r", encoding="utf-8") as f:
        return f.read()


@app.get("/health")
def health():
    return {"status": "ok", "service": "business-agents"}


@app.post("/leads/preview")
def preview_lead(lead: LeadRequest):
    return build_approval_queue([lead.model_dump()])[0]


@app.post("/approval/validate")
def validate_approval(request: ActionRequest):
    action = validate_action(request.action)
    return {"action": action, "approved": action == "approve"}


@app.post("/telegram/webhook")
async def telegram_webhook(request: Request):
    update = await request.json()
    message = extract_message(update)
    if not message:
        return {"ok": True, "handled": False}
    chat_id = message.get("chat", {}).get("id")
    photo = extract_photo(update)
    if photo and chat_id is not None:
        await send_message(chat_id, "📷 Photo received successfully. Send the business details or lead information you want the agents to work on.")
        return {"ok": True, "handled": True, "type": "photo", "file_id": photo.get("file_id")}
    text = message.get("text", "")
    if chat_id is not None and text:
        await send_message(chat_id, "🤖 Business Agents is online. Send a lead or a photo to begin.")
    return {"ok": True, "handled": True, "type": "message"}
