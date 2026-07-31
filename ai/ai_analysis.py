import os

from dotenv import load_dotenv
from openai import OpenAI
import json

from ai.prompts import LEAD_ANALYSIS_PROMPT
from ai.tech_stack import detect_tech_stack

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

MODEL = "llama-3.3-70b-versatile"


def analyze_lead(lead):

    prompt = LEAD_ANALYSIS_PROMPT.format(
        lead=lead
    )

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role":"user",
                "content":prompt
            }
        ]
    )

    content = response.choices[0].message.content

    return json.loads(content)

def build_lead_analysis(lead):

    combined_text = f"""
    {lead['website']}
    {lead['notes']}
    """

    tech_stack = detect_tech_stack(combined_text)

    report = analyze_lead(f"""
    Company: {lead['company']}
    Industry: {lead['industry']}
    Location: {lead['location']}
    Website: {lead['website']}

    Detected Technology Stack:
    {", ".join(tech_stack) if tech_stack else "Not detected"}

    Contact:
    {lead['contact']}

    Designation:
    {lead['designation']}

    Notes:
    {lead['notes']}
    """)

    report["tech_stack"] = tech_stack

    return report