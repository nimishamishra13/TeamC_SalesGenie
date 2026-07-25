from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/outreach", tags=["Outreach"])


class OutreachRequest(BaseModel):
    name: str
    company: str
    industry: str
    status: str


@router.post("/generate")
def generate_outreach(data: OutreachRequest):

    # Simple AI-like logic (rule-based for now)
    if data.industry.lower() == "tech":
        tone = "innovative and growth-focused"
    elif data.industry.lower() == "finance":
        tone = "professional and ROI-driven"
    else:
        tone = "friendly and engaging"

    message = f"""
Hi {data.name},

I came across {data.company} and was impressed by your work in the {data.industry} space.

We help companies like yours achieve better results through smart solutions. 
Given your current status as '{data.status}', I believe we can bring immediate value.

Would you be open to a quick discussion?

Best regards,  
Sales Team
"""

    return {
        "tone": tone,
        "message": message.strip()
    }