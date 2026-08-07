from fastapi import APIRouter
from pydantic import BaseModel
from services.conversation_service import analyze_transcript
from database.connection import SessionLocal
from database.models import Conversation
router = APIRouter(
    prefix="/conversation",
    tags=["Conversation Intelligence"]
)

class SaveConversationRequest(BaseModel):
    lead_id: int
    transcript: str
    summary: str
    sentiment: str
    buying_intent: str
    next_action: str
    crm_notes: str

class ConversationRequest(BaseModel):
    lead_id: int
    transcript: str


@router.get("/")
def health_check():
    return {
        "message": "Conversation Intelligence Module is Working!"
    }

@router.post("/analyze")
def analyze_conversation(request: ConversationRequest):

    return analyze_transcript(request.transcript)

@router.post("/save")
def save_conversation(request: SaveConversationRequest):

    db = SessionLocal()

    conversation = Conversation(
        lead_id=request.lead_id,
        transcript=request.transcript,
        summary=request.summary,
        sentiment=request.sentiment,
        buying_intent=request.buying_intent,
        next_action=request.next_action,
        crm_notes=request.crm_notes
    )

    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    db.close()

    return {
        "message": "Conversation saved successfully!",
        "conversation_id": conversation.id
    }
