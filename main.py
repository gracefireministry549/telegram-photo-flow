"""Business Agents API and Telegram webhook."""
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from app.pipeline import build_approval_queue
from app.approval import validate_action
from app.telegram import extract_message, extract_photo, send_message

app = FastAPI(title="Business Agents")

DASHBOARD = """<!doctype html>
<html><head><meta name='viewport' content='width=device-width,initial-scale=1'>
<title>Business Agents</title>
<style>body{font-family:Arial;margin:0;background:#f5f7fb;color:#172033}main{max-width:900px;margin:auto;padding:24px}.hero{background:#172033;color:white;padding:24px;border-radius:18px}h1{margin:0 0 8px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px;margin-top:16px}.card{background:white;padding:18px;border-radius:14px;box-shadow:0 2px 10px #0001}.ok{font-weight:bold}.flow{line-height:2.1}.note{color:#596579}</style></head>
<body><main><section class='hero'><h1>🤖 Business Agents</h1><div>Your AI-assisted business lead and problem-solving control center</div></section>
<div class='grid'><div class='card'><h3>🔎 Scout</h3><p>Finds relevant public business opportunities.</p></div><div class='card'><h3>🕵️ Detective</h3><p>Checks evidence and identifies the business problem.</p></div><div class='card'><h3>🛠️ Solver</h3><p>Designs a practical solution and job plan.</p></div><div class='card'><h3>📣 Marketer</h3><p>Prepares personalized outreach for your approval.</p></div></div>
<div class='card' style='margin-top:16px'><h2>Approval workflow</h2><div class='flow'>Lead found → Problem verified → Solution proposed → <b>YOU APPROVE</b> → Client contact → Job → Completion proof → Report</div><p class='note'>The system will not contact a lead just because it found one. External outreach requires your approval.</p></div>
<div class='card' style='margin-top:16px'><h2>System status</h2><p class='ok'>🟢 API online</p><p>Telegram: awaiting secure bot token + webhook setup</p><p>Lead pipeline: ready</p><p>Approval gate: ready</p></div></main></body></html>"""


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
    return DASHBOARD


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
