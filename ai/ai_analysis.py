import os
import json

from dotenv import load_dotenv
from openai import OpenAI

from ai.prompts import LEAD_ANALYSIS_PROMPT


load_dotenv()


GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise RuntimeError(
        "GROQ_API_KEY is not configured in the .env file."
    )


MODEL = os.getenv(
    "GROQ_MODEL",
    "openai/gpt-oss-20b"
)


client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)


def analyze_lead(lead):

    prompt = LEAD_ANALYSIS_PROMPT.format(
        lead=lead
    )

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    content = response.choices[0].message.content

    try:
        return json.loads(content)

    except json.JSONDecodeError as e:

        raise ValueError(
            f"AI returned invalid JSON: {content}"
        ) from e