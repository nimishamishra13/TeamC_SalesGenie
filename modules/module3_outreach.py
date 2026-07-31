from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database.connection import get_db
from database.models import OutreachHistory


router = APIRouter(
    prefix="/outreach",
    tags=["Outreach"]
)


class OutreachRequest(BaseModel):

    lead_id: int
    name: str
    company: str
    industry: str
    status: str



@router.post("/generate")
def generate_outreach(
    data: OutreachRequest,
    db: Session = Depends(get_db)
):

    # Decide tone

    if data.industry.lower() == "tech":

        tone = "innovative and growth-focused"

    elif data.industry.lower() == "finance":

        tone = "professional and ROI-driven"

    else:

        tone = "friendly and engaging"



    # Generate outreach message

    message = f"""
Hi {data.name},

I came across {data.company} and was impressed by your work in the {data.industry} space.

We help companies like yours achieve better results through smart AI-powered solutions.

Given your current status as '{data.status}', I believe we can bring immediate value.

Would you be open to a quick discussion?

Best regards,
Sales Team
"""


    message = message.strip()



    # Save outreach activity

    outreach_record = OutreachHistory(

        lead_id=data.lead_id,

        company=data.company,

        industry=data.industry,

        message=message,

        tone=tone

    )


    db.add(outreach_record)

    db.commit()

    db.refresh(outreach_record)



    return {

        "message":
        "Outreach generated and saved successfully",

        "outreach_id":
        outreach_record.id,

        "lead_id":
        data.lead_id,

        "tone":
        tone,

        "generated_message":
        message

    }
