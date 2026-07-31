from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database.connection import get_db
from database.models import Conversation, CRMActivity

from modules.module5_ai import analyze_conversation


router = APIRouter()



class ConversationRequest(BaseModel):

    lead_id: int

    conversation_type: str

    transcript: str



@router.post("/conversation/analyze")
def analyze_sales_conversation(
    data: ConversationRequest,
    db: Session = Depends(get_db)
):

    # AI Analysis
    ai_result = analyze_conversation(
        data.transcript
    )


    # Save Conversation
    conversation = Conversation(

        lead_id=data.lead_id,

        conversation_type=data.conversation_type,

        transcript=data.transcript,

        summary=ai_result,

        key_points=ai_result,

        action_items=ai_result

    )


    db.add(conversation)

    db.commit()

    db.refresh(conversation)



    # CRM Sync
    crm_activity = CRMActivity(

        lead_id=data.lead_id,

        activity_type="Conversation Analysis",

        description=ai_result,

        status="Synced"

    )


    db.add(crm_activity)

    db.commit()

    db.refresh(crm_activity)



    # Response
    return {

        "message":
        "Conversation analyzed and CRM synced successfully",

        "conversation_id":
        conversation.id,

        "crm_activity_id":
        crm_activity.id,

        "lead_id":
        data.lead_id,

        "crm_status":
        "Synced",

        "analysis":
        ai_result

    }
