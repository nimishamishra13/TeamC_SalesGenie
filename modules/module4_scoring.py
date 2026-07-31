from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/ai", tags=["AI Scoring"])


class ScoreRequest(BaseModel):
    company: str
    status: str
    industry: str


@router.post("/score")
def score_lead(data: ScoreRequest):

    score = 50  # base score

    # Status impact
    if data.status == "converted":
        score += 40
    elif data.status == "contacted":
        score += 20

    # Industry impact
    if data.industry == "tech":
        score += 10
    elif data.industry == "finance":
        score += 5

    # Cap score
    score = min(score, 100)

    # Recommendation logic
    if score > 80:
        action = "Close deal immediately"
    elif score > 60:
        action = "Schedule meeting"
    elif score > 40:
        action = "Send follow-up email"
    else:
        action = "Cold outreach needed"

    return {
        "score": score,
        "recommendation": action
    }