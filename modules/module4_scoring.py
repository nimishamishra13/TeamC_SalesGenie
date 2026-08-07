from fastapi import APIRouter
from pydantic import BaseModel
import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from modules.ml.feature_engineering import extract_features
from modules.ml.predict import predict_lead as ml_predict
router = APIRouter(prefix="/score", tags=["AI Lead Scoring"])

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

MODEL = "llama-3.3-70b-versatile"

class ScoreRequest(BaseModel):
    name: str
    company: str
    industry: str
    status: str
    notes: str = ""
    analysis: str = ""

@router.post("/predict")
def predict_lead(data: ScoreRequest):
    lead = {
    "company": data.company,
    "industry": data.industry,
    "status": data.status,
    "notes": data.notes
    }
    analysis = json.loads(data.analysis)
    features = extract_features(
        lead,
        analysis
    )
    print(features)
    prediction = ml_predict(features)

    lead_score = prediction["lead_score"]

    conversion_probability = prediction["conversion_probability"]
    print(prediction)
    prompt = f"""
        You are an expert AI-powered CRM Lead Scoring Assistant used by Infosys.

        Your task is to analyze the lead information and estimate the likelihood of converting this lead into a customer.

        Lead Details:

        Name: {data.name}
        Company: {data.company}
        Industry: {data.industry}
        Current Status: {data.status}
        Notes: {data.notes}
        Previous AI Analysis: {data.analysis}

        Instructions:

        Analyze the lead carefully.

        
        Machine Learning Prediction

            Lead Score:
            {lead_score}

            Conversion Probability:
            {conversion_probability}%

            Using the ML prediction above,

            Generate:

            1. Priority
            2. Confidence
            3. Next Best Action
            4. Professional business reasoning.
        Scoring Guidelines:

        - Higher scores should indicate stronger conversion potential.
        - Consider industry relevance, lead status, and notes.
        - Recommendations should be practical and business-oriented.
        Provide 2 to 3 concise sentences explaining why this lead received the assigned score so that it looks professional as well as detailed.
        The next best action should be specific and actionable.

        Examples:

        - Schedule a product demo within 48 hours.
        - Assign the lead to a senior sales representative.
        - Share a case study relevant to the industry.
        - Send pricing information.
        - Continue nurturing through email.
        Do not use the contact person's name in the next best action.
        Write the recommendation as a business action for the sales team.
        Estimate the confidence level as Low, Medium, High, or Very High.

        Return ONLY valid JSON in this format:

        {{
            "priority": "",
            "confidence": "",
            "next_best_action": "",
            "reason": ""
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
        temperature=0.3,
        response_format={"type": "json_object"}
    )
    content = response.choices[0].message.content       

    llm_output = json.loads(content)

    return {
        "lead_score": lead_score,
        "conversion_probability": conversion_probability,
        **llm_output
    }
