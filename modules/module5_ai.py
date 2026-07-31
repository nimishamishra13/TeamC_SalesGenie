# modules/module5_ai.py

from groq import Groq
import os
from dotenv import load_dotenv


# Load environment variables from .env
load_dotenv()


# Get Groq API Key
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


# Check API Key
if not GROQ_API_KEY:
    raise ValueError(
        "GROQ_API_KEY is missing. Add it to your .env file."
    )


# Initialize Groq Client
client = Groq(
    api_key=GROQ_API_KEY
)



def analyze_conversation(transcript):


    prompt = f"""

You are SalesGenie AI, an intelligent sales assistant.

Analyze the following sales conversation.

Provide:

1. Conversation Summary

2. Key Discussion Points

3. Customer Requirements

4. Action Items

5. Follow-up Suggestions


Sales Conversation:

{transcript}


Give a clear and professional response.

"""


    response = client.chat.completions.create(

        model="llama-3.1-8b-instant",

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0.3
    )


    return response.choices[0].message.content
