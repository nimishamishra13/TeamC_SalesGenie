from fastapi import APIRouter
from pydantic import BaseModel

import os
import json

from dotenv import load_dotenv
from openai import OpenAI


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/outreach",
    tags=["Outreach"]
)


# ============================================================
# GROQ CLIENT
# ============================================================

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

# Faster model for Outreach Generation
MODEL = "openai/gpt-oss-20b"

# ============================================================
# INDUSTRY-SPECIFIC GUIDANCE
# ============================================================

INDUSTRY_PROMPTS = {

    "technology": """
Focus on:
- AI adoption
- Cloud migration
- Application modernization
- Cybersecurity
- Digital transformation
""",

    "finance": """
Focus on:
- Regulatory compliance
- Risk management
- Fraud detection
- Data security
- Cost optimization
""",

    "healthcare": """
Focus on:
- Patient experience
- Digital health
- Healthcare analytics
- Data privacy
- Hospital efficiency
""",

    "manufacturing": """
Focus on:
- Industry 4.0
- Supply chain optimization
- Predictive maintenance
- Smart factories
- Automation
""",

    "retail": """
Focus on:
- Customer experience
- Personalized shopping
- Omnichannel retail
- Inventory optimization
- Demand forecasting
""",

    "education": """
Focus on:
- Digital learning
- Student engagement
- AI-powered education
- Learning analytics
- Cloud infrastructure
"""
}


# ============================================================
# REQUEST MODEL
# ============================================================

class OutreachRequest(BaseModel):

    name: str
    company: str
    industry: str
    status: str

    analysis: str = ""
    score: int = 0


# ============================================================
# OUTREACH GENERATION
# ============================================================

@router.post("/generate")
def generate_outreach(data: OutreachRequest):

    industry_prompt = INDUSTRY_PROMPTS.get(
        data.industry.lower(),
        """
Focus on:
- Business growth
- Operational efficiency
- Digital transformation
"""
    )

    # --------------------------------------------------------
    # PROMPT
    # --------------------------------------------------------

    prompt = f"""
You are an Enterprise Sales Consultant at Infosys.

Create a highly personalized B2B outreach email for the lead below.

Lead Information:

Company: {data.company}
Contact Person: {data.name}
Industry: {data.industry}
Lead Status: {data.status}
Lead Score: {data.score}

Industry Guidance:
{industry_prompt}

AI Lead Analysis:
{data.analysis}

Requirements:

- Personalize the email specifically for the company.
- Use the business opportunities and technology needs identified
  in the AI Lead Analysis.
- Explain briefly how Infosys can help.
- Keep the tone professional and consultative.
- Avoid generic sales language.
- Do not invent facts that are not present in the lead analysis.
- Keep the email between 100 and 130 words.
- Include a greeting.
- Use 3 short paragraphs.
- End with a clear request for a short meeting.
- End with:

Best Regards,
Infosys Sales Team

Do not generate talking points.

Return ONLY valid JSON with exactly these fields:

{{
    "tone": "...",
    "subject": "...",
    "message": "..."
}}

The message must use \\n for line breaks.

Do not include markdown.
Do not include explanations.
Do not include any additional fields.
"""


    # --------------------------------------------------------
    # LLM CALL
    # --------------------------------------------------------


    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an enterprise B2B sales email generator. "
                    "Generate concise personalized sales emails."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2,
        max_tokens=500,
        reasoning_effort="low",
        response_format={"type": "json_object"}
    )

    content = (
        response.choices[0].message.content or ""
    ).strip()

    if not content:
        raise ValueError(
            "M3 returned an empty response. "
            f"finish_reason={response.choices[0].finish_reason}"
        )

    try:
        result = json.loads(content)

    except json.JSONDecodeError:

        start = content.find("{")
        end = content.rfind("}")

        if start == -1 or end == -1:
            raise ValueError(
                f"M3 returned invalid JSON: {content}"
            )

        result = json.loads(
            content[start:end + 1]
        )

    required_fields = [
        "tone",
        "subject",
        "message"
    ]

    for field in required_fields:

        if field not in result:
            raise ValueError(
                f"M3 response missing field: {field}"
            )

    return {
        "tone": result["tone"],
        "subject": result["subject"],
        "message": result["message"]
    }
