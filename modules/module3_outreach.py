from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/outreach", tags=["Outreach"])
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

MODEL = "llama-3.3-70b-versatile"

class OutreachRequest(BaseModel):
    name: str
    company: str
    industry: str
    status: str

    analysis: str = ""
    score: int = 0

@router.post("/generate")
def generate_outreach(data: OutreachRequest):

    prompt = f"""
        You are an experienced Enterprise Sales Consultant at Infosys.

        Your task is to generate a highly personalized outreach package for a potential client based on the AI lead analysis.

        Lead Details

        Company: {data.company}

        Contact Person: {data.name}

        Industry: {data.industry}

        Lead Status: {data.status}

        Lead Score:
        {data.score}

        AI Lead Analysis:
        {data.analysis}

        Instructions:

        - Carefully analyze the lead information and AI analysis before writing.
        - Personalize the email specifically for this company.
        - Mention challenges or opportunities identified in the AI analysis whenever appropriate.
        - Explain how Infosys can help solve those business challenges.
        - Keep the email professional, consultative, and concise.
        - Avoid generic sales language or exaggerated marketing claims.
        - End the email with a clear call-to-action requesting a short meeting.
       
        Email Formatting Requirements:

        - Begin with a greeting (e.g., Dear Rahul,).
        - Leave one blank line after the greeting.
        - Split the email into 3–4 short paragraphs.
        - Each paragraph should contain 2–3 sentences.
        - End with a professional closing such as:

        Best Regards,
        Infosys Sales Team
        Return valid JSON only.
        In the "message" field, represent line breaks using escaped newline characters (\\n), not literal line breaks.
        Generate:

        1. A suitable outreach tone.
        2. A compelling email subject.
        3. A personalized outreach email (150–200 words).
        4. Four concise talking points that a sales representative can use during the meeting.

        Return ONLY valid JSON in the following format:

        {{
            "tone": "...",
            "subject": "...",
            "message": "...",
            "talking_points": [
                "...",
                "...",
                "...",
                "..."
            ]
        }}

        Do not include markdown.
        Do not include explanations.
        Return only valid JSON.
        """

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.7,
        response_format={"type": "json_object"}
    )
    content = response.choices[0].message.content

    import json

    return json.loads(content)