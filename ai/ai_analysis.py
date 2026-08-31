import os
import json

from dotenv import load_dotenv
from openai import OpenAI

from ai.prompts import LEAD_ANALYSIS_PROMPT
from ai.tech_stack import detect_tech_stack


load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

MODEL = "openai/gpt-oss-120b"

def analyze_lead(lead):

    prompt = LEAD_ANALYSIS_PROMPT.format(
        lead=lead
    )

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a concise B2B sales intelligence assistant. "
                    "Use minimal reasoning and return the final JSON directly."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.1,
        max_tokens=700,
        reasoning_effort="low"
    )

    choice = response.choices[0]

    content = (
        choice.message.content or ""
    ).strip()

    print("🔥 M2 FINISH REASON:", choice.finish_reason)
    print("🔥 M2 CONTENT:", repr(content))

    if not content:
        raise ValueError(
            f"M2 returned an empty response. "
            f"finish_reason={choice.finish_reason}"
        )

    if content.startswith("```"):
        content = content.replace("```json", "")
        content = content.replace("```", "")
        content = content.strip()

    try:
        return json.loads(content)

    except json.JSONDecodeError:

        start = content.find("{")
        end = content.rfind("}")

        if start != -1 and end != -1:

            try:
                return json.loads(
                    content[start:end + 1]
                )
            except json.JSONDecodeError:
                pass

        raise ValueError(
            f"M2 returned invalid JSON: {content}"
        )
def build_lead_analysis(lead):

    combined_text = f"""
{lead.get('website', '')}
{lead.get('notes', '')}
"""

    tech_stack = detect_tech_stack(
        combined_text
    )

    lead_text = f"""
Company: {lead.get('company', '')}
Industry: {lead.get('industry', '')}
Location: {lead.get('location', '')}
Website: {lead.get('website', '')}

Detected Technology Stack:
{", ".join(tech_stack) if tech_stack else "Not detected"}

Contact: {lead.get('contact', '')}
Designation: {lead.get('designation', '')}

Notes:
{lead.get('notes', '')}
"""

    report = analyze_lead(lead_text)

    report["tech_stack"] = tech_stack

    return report
