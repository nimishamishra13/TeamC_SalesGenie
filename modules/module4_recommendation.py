from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(
    prefix="/recommendation",
    tags=["Recommendation Engine"]
)


class RecommendationRequest(BaseModel):
    industry: str
    company: str
    company_size: str = "Unknown"
    lead_status: str
    lead_score: int
    conversion_probability: float
    engagement_score: int = 0
    tech_stack_match: int = 0
    budget_score: int = 0


@router.post("/predict")
def generate_recommendation(data: RecommendationRequest):

    # -----------------------------
    # FOLLOW-UP TIMING
    # -----------------------------

    if data.lead_score >= 80 and data.engagement_score >= 70:
        follow_up_timing = "Within 24–48 hours"

    elif data.lead_score >= 60:
        follow_up_timing = "Within 3–5 days"

    else:
        follow_up_timing = "Within 1–2 weeks"

    # -----------------------------
        # PRIORITY
        # -----------------------------

    if data.lead_score >= 80 and data.engagement_score >= 70:
            priority = "High"

    elif data.lead_score >= 60 and data.engagement_score >= 50:
            priority = "Medium"

    else:
            priority = "Low"

    # -----------------------------
    # CHANNEL MIX
    # -----------------------------

    if data.lead_score >= 80:
        primary_channel = "Email"
        secondary_channel = "Phone Call"

    elif data.engagement_score >= 60:
        primary_channel = "Email"
        secondary_channel = "LinkedIn"

    else:
        primary_channel = "Email"
        secondary_channel = "LinkedIn"


    # -----------------------------
    # CONTENT STRATEGY
    # -----------------------------

    if data.industry.lower() == "technology":
        content_strategy = (
            "Focus on technology adoption, scalability, "
            "integration capabilities, and measurable business value."
        )

    elif data.industry.lower() == "finance":
        content_strategy = (
            "Focus on security, compliance, operational efficiency, "
            "and measurable business outcomes."
        )

    elif data.industry.lower() == "healthcare":
        content_strategy = (
            "Focus on security, reliability, workflow improvement, "
            "and operational efficiency."
        )

    else:
        content_strategy = (
            "Focus on business value, relevant use cases, "
            "efficiency improvements, and ROI."
        )


    # -----------------------------
    # REASON
    # -----------------------------

    reasons = []

    if data.lead_score >= 80:
        reasons.append("strong lead score")

    if data.engagement_score >= 70:
        reasons.append("high engagement")

    if data.tech_stack_match >= 70:
        reasons.append("strong technology fit")

    if data.budget_score >= 70:
        reasons.append("positive budget alignment")

    if not reasons:
        reasons.append("available lead and engagement signals")


    reason = (
        "Recommendation based on "
        + ", ".join(reasons)
        + "."
    )


    return {
        "priority": priority,
        "follow_up_timing": follow_up_timing,
        "primary_channel": primary_channel,
        "secondary_channel": secondary_channel,
        "content_strategy": content_strategy,
        "reason": reason
    }
