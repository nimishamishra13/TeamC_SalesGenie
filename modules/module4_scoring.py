from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database.connection import get_db
from database.models import LeadScore



router = APIRouter(
    prefix="/ai",
    tags=["AI Scoring"]
)



class ScoreRequest(BaseModel):

    lead_id: int
    company: str
    status: str
    industry: str




@router.post("/score")
def score_lead(
    data: ScoreRequest,
    db: Session = Depends(get_db)
):


    score = 50



    # Status based scoring

    if data.status == "converted":

        score += 40


    elif data.status == "contacted":

        score += 20



    elif data.status == "qualified":

        score += 30



    # Industry scoring

    if data.industry.lower() == "tech":

        score += 10


    elif data.industry.lower() == "finance":

        score += 5



    # Maximum score

    score = min(score,100)



    # Recommendation

    if score >= 80:

        recommendation = (
            "High priority lead. "
            "Close deal immediately."
        )


    elif score >= 60:

        recommendation = (
            "Warm lead. "
            "Schedule meeting."
        )


    elif score >= 40:

        recommendation = (
            "Follow up with personalized outreach."
        )


    else:

        recommendation = (
            "Cold lead. "
            "Start awareness campaign."
        )



    # Save scoring history

    score_record = LeadScore(

        lead_id=data.lead_id,

        company=data.company,

        industry=data.industry,

        score=score,

        recommendation=recommendation

    )


    db.add(score_record)

    db.commit()

    db.refresh(score_record)



    return {

        "message":
        "Lead score generated and saved successfully",

        "score_id":
        score_record.id,

        "lead_id":
        data.lead_id,

        "company":
        data.company,

        "score":
        score,

        "recommendation":
        recommendation

    }
