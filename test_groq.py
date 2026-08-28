import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv(override=True)

api_key = os.getenv("GROQ_API_KEY")
model = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")

if not api_key:
    raise RuntimeError("GROQ_API_KEY is missing")

print("API key loaded:", True)
print("Model:", model)

client = OpenAI(
    api_key=api_key,
    base_url="https://api.groq.com/openai/v1"
)

response = client.chat.completions.create(
    model=model,
    messages=[
        {
            "role": "user",
            "content": "Say hello in one sentence."
        }
    ],
    temperature=0
)

print("Response:")
print(response.choices[0].message.content)
