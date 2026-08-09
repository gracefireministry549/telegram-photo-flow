"""Minimal HTTP API for the business-agent approval workflow."""
from fastapi import FastAPI
from pydantic import BaseModel, Field
from app.pipeline import build_approval_queue
from app.approval import validate_action

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


@app.get("/")
def health():
    return {"status": "ok", "service": "business-agents"}


@app.post("/leads/preview")
def preview_lead(lead: LeadRequest):
    """Create an approval-ready preview; this does not contact the lead."""
    return build_approval_queue([lead.model_dump()])[0]


@app.post("/approval/validate")
def validate_approval(request: ActionRequest):
    return {"action": validate_action(request.action), "approved": request.action.lower() == "approve"}
