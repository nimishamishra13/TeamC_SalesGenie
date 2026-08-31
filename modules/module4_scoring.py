from fastapi import APIRouter
from pydantic import BaseModel

import os
import json

from dotenv import load_dotenv
from openai import OpenAI

from modules.ml.feature_engineering import extract_features
from modules.ml.interaction_scoring import (
    calculate_interaction_adjustment
)

from database.connection import SessionLocal
from database.models import Conversation, Lead


router = APIRouter(
    prefix="/score",
    tags=["AI Lead Scoring"]
)


# ==========================================================
# OPENAI / GROQ
# ==========================================================

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

MODEL = "openai/gpt-oss-120b"

# ==========================================================
# REQUEST MODEL
# ==========================================================

class ScoreRequest(BaseModel):

    lead_id: int
    name: str
    company: str
    industry: str
    status: str

    designation: str = ""
    website: str = ""
    location: str = ""
    notes: str = ""

    analysis: str = ""

def generate_fast_recommendation(
    final_score,
    ai_status,
    sentiment,
    buying_intent,
    next_actions,
    interaction_adjustment
):

    # ------------------------------------------------------
    # FOLLOW-UP TIMING
    # ------------------------------------------------------

    if buying_intent == "high" or final_score >= 75:
        follow_up_timing = "Within 24 hours"

    elif buying_intent == "medium" or final_score >= 50:
        follow_up_timing = "Within 48 hours"

    else:
        follow_up_timing = "Within 1 week"


    # ------------------------------------------------------
    # PRIMARY CHANNEL
    # ------------------------------------------------------

    if buying_intent == "high":

        primary_channel = "Phone Call"

    elif sentiment == "positive":

        primary_channel = "Email"

    elif sentiment == "neutral":

        primary_channel = "LinkedIn"

    else:

        primary_channel = "Email"


    # ------------------------------------------------------
    # SECONDARY CHANNEL
    # ------------------------------------------------------

    if primary_channel == "Phone Call":

        secondary_channel = "Email"

    elif primary_channel == "Email":

        secondary_channel = "Phone Call"

    else:

        secondary_channel = "Email"


    # ------------------------------------------------------
    # CONTENT STRATEGY
    # ------------------------------------------------------

    if buying_intent == "high":

        content_strategy = (
            "Prioritize a direct sales conversation focused on the "
            "prospect's immediate business priorities. Present a "
            "tailored solution, address identified concerns, and "
            "propose a clear technical or discovery meeting."
        )

    elif sentiment == "positive":

        content_strategy = (
            "Use a consultative message that connects Infosys "
            "capabilities to the prospect's identified opportunities. "
            "Share relevant value propositions and suggest a focused "
            "follow-up discussion."
        )

    elif sentiment == "negative":

        content_strategy = (
            "Address the prospect's concerns before pushing for "
            "further engagement. Provide relevant clarification, "
            "evidence, and a low-pressure next step."
        )

    else:

        content_strategy = (
            "Use a concise, value-focused message highlighting "
            "relevant Infosys capabilities and invite the prospect "
            "to discuss their requirements."
        )


    # ------------------------------------------------------
    # REASON
    # ------------------------------------------------------

    reasons = []

    if final_score >= 75:
        reasons.append(
            f"High lead score of {final_score}/100"
        )

    if buying_intent == "high":
        reasons.append(
            "High buying intent"
        )

    if sentiment == "positive":
        reasons.append(
            "Positive conversation sentiment"
        )

    if next_actions:
        reasons.append(
            "Clear next action identified"
        )

    if interaction_adjustment > 0:
        reasons.append(
            "Positive conversation signals increased engagement"
        )

    if not reasons:
        reasons.append(
            "Recommendation based on current lead signals"
        )


    return {

        "follow_up_timing":
            follow_up_timing,

        "primary_channel":
            primary_channel,

        "secondary_channel":
            secondary_channel,

        "content_strategy":
            content_strategy,

        "reason":
            ". ".join(reasons) + "."
    }
# ==========================================================
# SCORE API
# ==========================================================

@router.post("/predict")
def predict_lead(
    data: ScoreRequest,
    use_llm_recommendation: bool = True
):
    print("🔥 SCORE API CALLED")
    print("Lead ID:", data.lead_id)
    print("Company:", data.company)

    # ======================================================
    # 1. PREPARE LEAD DATA
    # ======================================================

    lead_data = {

        "name": data.name,

        "company": data.company,

        "industry": data.industry,

        "status": data.status,

        "designation": data.designation,

        "website": data.website,

        "location": data.location,

        "notes": data.notes
    }

    # ======================================================
    # 2. PARSE AI ANALYSIS
    # ======================================================

    try:

        analysis_data = (
            json.loads(data.analysis)
            if data.analysis
            else {}
        )

    except json.JSONDecodeError:

        analysis_data = {}

    # ======================================================
    # 3. FEATURE ENGINEERING
    # ======================================================

    features = extract_features(
        lead_data,
        analysis_data
    )

    print(
        "🔥 FEATURES USED FOR SCORING:",
        features
    )

    # ======================================================
    # 4. GET LATEST CONVERSATION
    # ======================================================

    db = SessionLocal()

    latest_conversation = (

        db.query(Conversation)

        .filter(
            Conversation.lead_id == data.lead_id
        )

        .order_by(
            Conversation.id.desc()
        )

        .first()
    )

    db.close()

    # ======================================================
    # 5. BUILD CONVERSATION DATA
    # ======================================================

    if latest_conversation:

        conversation_data = {

            "sentiment":
                latest_conversation.sentiment,

            "buying_intent":
                latest_conversation.buying_intent,

            "objections": [],

            "pain_points": [],

            "next_actions": [

                latest_conversation.next_action

            ]
            if latest_conversation.next_action
            else [],

            "crm_notes":
                latest_conversation.crm_notes or ""
        }

    else:

        conversation_data = {}

    # ======================================================
    # 6. CONVERSATION INTELLIGENCE
    # ======================================================

    interaction_result = (
        calculate_interaction_adjustment(
            conversation_data
        )
    )

    interaction_adjustment = (
        interaction_result["adjustment"]
    )

    # Limit contribution to 15 points
    interaction_adjustment = max(
        -15,
        min(
            15,
            interaction_adjustment
        )
    )

    # ======================================================
    # 7. COMPANY PROFILE SCORE
    # ======================================================

    company_size = features.get(
        "company_size",
        "SMB"
    )

    if company_size == "Enterprise":

        company_size_score = 15

    elif company_size == "Mid-Market":

        company_size_score = 10

    else:

        company_size_score = 7

    # ======================================================
    # 8. DECISION MAKER SCORE
    # ======================================================

    decision_maker_score = features.get(
        "decision_maker_score",
        3
    )

    # Maximum = 15
    decision_maker_score = min(
        decision_maker_score,
        15
    )

    # ======================================================
    # 9. CRM / PROFILE SCORE
    # ======================================================

    crm_profile_score = (
        company_size_score
        +
        decision_maker_score
    )

    # Maximum = 30
    #
    # But our final allocation gives
    # Company Profile 15 + Decision Maker 15.
    #
    # Therefore this is already correctly bounded.
    # ======================================================


    # ======================================================
    # 10. INDUSTRY FIT
    # ======================================================

    technology_industries = [

        "technology",
        "software",
        "it services",
        "information technology"
    ]

    if data.industry.lower().strip() in (
        technology_industries
    ):

        industry_fit_score = 10

    else:

        industry_fit_score = 7


    # ======================================================
    # 11. TECHNOLOGY FIT
    # ======================================================

    tech_stack_match = features.get(
        "tech_stack_match",
        0
    )

    technology_fit_score = round(
        (tech_stack_match / 100) * 20,
        2
    )

    # ======================================================
    # 12. BUDGET FIT
    # ======================================================

    budget_score = features.get(
        "budget_score",
        60
    )

    budget_component = round(
        (budget_score / 100) * 10,
        2
    )

    # ======================================================
    # 13. ACTUAL ENGAGEMENT
    # ======================================================
    #
    # IMPORTANT:
    # Engagement is NOT based on Hot/Warm/Cold.
    #
    # It is based on actual conversation signals.
    # ======================================================

    engagement_component = 0

    sentiment = (
        conversation_data
        .get("sentiment", "")
        .lower()
        .strip()
    )

    buying_intent = (
        conversation_data
        .get("buying_intent", "")
        .lower()
        .strip()
    )

    next_actions = conversation_data.get(
        "next_actions",
        []
    )

    # Sentiment contribution: 0-7
    if sentiment == "positive":

        engagement_component += 7

    elif sentiment == "neutral":

        engagement_component += 4

    elif sentiment == "negative":

        engagement_component += 1

    # Buying intent contribution: 0-6
    if buying_intent == "high":

        engagement_component += 6

    elif buying_intent == "medium":

        engagement_component += 4

    elif buying_intent == "low":

        engagement_component += 1

    # Clear next action
    if next_actions:

        engagement_component += 2

    # Maximum 15
    engagement_component = min(
        engagement_component,
        15
    )

    # ======================================================
    # 14. BASE SCORE
    # ======================================================

    base_score = (

        company_size_score

        +

        decision_maker_score

        +

        technology_fit_score

        +

        industry_fit_score

        +

        budget_component

        +

        engagement_component
    )

    # ======================================================
    # 15. FINAL AI SCORE
    # ======================================================

    final_score = round(
        base_score
        +
        interaction_adjustment
    )

    final_score = max(
        0,
        min(
            100,
            final_score
        )
    )

    # ======================================================
    # 16. DETERMINE LEAD STATUS
    # ======================================================
    #
    # THIS IS NOW THE OUTPUT OF AI SCORING.
    #
    # CRM status is NOT used to calculate the score.
    # ======================================================

    if final_score >= 75:

        ai_status = "Hot"

    elif final_score >= 50:

        ai_status = "Warm"

    else:

        ai_status = "Cold"

    # ======================================================
    # 17. UPDATE DATABASE
    # ======================================================

    db = SessionLocal()

    lead = (
        db.query(Lead)
        .filter(
            Lead.id == data.lead_id
        )
        .first()
    )

    if lead:

        lead.score = int(
            final_score
        )

        lead.ai_status = ai_status

        db.commit()

    db.close()

    # ======================================================
    # 18. DEBUG OUTPUT
    # ======================================================

    print(
        "🔥 SCORE BREAKDOWN:"
    )

    print(
        "Company Size:",
        company_size_score
    )

    print(
        "Decision Maker:",
        decision_maker_score
    )

    print(
        "Technology Fit:",
        technology_fit_score
    )

    print(
        "Industry Fit:",
        industry_fit_score
    )

    print(
        "Budget:",
        budget_component
    )

    print(
        "Engagement:",
        engagement_component
    )

    print(
        "Base Score:",
        base_score
    )

    print(
        "Interaction Adjustment:",
        interaction_adjustment
    )

    print(
        "🔥 FINAL AI LEAD SCORE:",
        final_score
    )

    print(
        "🔥 AI LEAD STATUS:",
        ai_status
    )

        # ======================================================
    # 19. RECOMMENDATION ENGINE
    # ======================================================

    sentiment = (
        conversation_data
        .get("sentiment", "")
        .lower()
        .strip()
    )

    buying_intent = (
        conversation_data
        .get("buying_intent", "")
        .lower()
        .strip()
    )

    next_actions = conversation_data.get(
        "next_actions",
        []
    )

    if use_llm_recommendation:

        recommendation_prompt = f"""

You are an enterprise sales recommendation engine
for Infosys.

Analyze the lead using the AI lead scoring results.

Company:
{data.company}

Industry:
{data.industry}

Designation:
{data.designation}

Notes:
{data.notes}

AI Lead Score:
{final_score} / 100

AI Lead Status:
{ai_status}

Scoring Breakdown:

Company Profile:
{company_size_score} / 15

Decision Maker:
{decision_maker_score} / 15

Technology Fit:
{technology_fit_score} / 20

Industry Fit:
{industry_fit_score} / 10

Budget:
{budget_component} / 10

Engagement:
{engagement_component} / 15

Conversation Intelligence:
{interaction_adjustment} points

Conversation Sentiment:
{sentiment}

Buying Intent:
{buying_intent}

Determine:

1. Follow-up timing
2. Primary communication channel
3. Secondary communication channel
4. Content strategy
5. Reason for recommendation

Do NOT generate an email.

Do NOT use the contact person's name.

Return ONLY valid JSON:

{{
    "follow_up_timing": "",
    "primary_channel": "",
    "secondary_channel": "",
    "content_strategy": "",
    "reason": ""
}}

Do not include markdown.
Do not include explanations outside the JSON.
"""

        recommendation_response = (
            client.chat.completions.create(

                model=MODEL,

                messages=[
                    {
                        "role": "user",
                        "content": recommendation_prompt
                    }
                ],

                temperature=0.3,

                response_format={
                    "type": "json_object"
                }
            )
        )

        recommendation = json.loads(
            recommendation_response
            .choices[0]
            .message
            .content
        )

    else:

        recommendation = generate_fast_recommendation(

            final_score=final_score,

            ai_status=ai_status,

            sentiment=sentiment,

            buying_intent=buying_intent,

            next_actions=next_actions,

            interaction_adjustment=interaction_adjustment
        )

    # ======================================================
    # 20. RETURN RESPONSE
    # ======================================================

    return {

        "lead_score": final_score,

        "lead_status": ai_status,

        "score_breakdown": {

            "company_profile":
                company_size_score,

            "decision_maker":
                decision_maker_score,

            "technology_fit":
                technology_fit_score,

            "industry_fit":
                industry_fit_score,

            "budget":
                budget_component,

            "engagement":
                engagement_component,

            "conversation_intelligence":
                interaction_adjustment
        },

        "interaction_adjustment":
            interaction_adjustment,

        "interaction_reasons":
            interaction_result["reasons"],

        "recommendation":
            recommendation
    }
