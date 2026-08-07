import os
import joblib
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

model = joblib.load(os.path.join(BASE_DIR, "model.pkl"))
encoders = joblib.load(os.path.join(BASE_DIR, "label_encoders.pkl"))


def predict_lead(features):

    df = pd.DataFrame([features])

    # Encode categorical columns
    for col in ["industry", "company_size", "lead_status"]:
        df[col] = encoders[col].transform(df[col])

    probability = model.predict_proba(df)[0][1]

    lead_score = int(probability * 100)

    return {
        "conversion_probability": round(probability * 100, 2),
        "lead_score": lead_score
    }
if __name__ == "__main__":

    sample = {
        "industry": "Technology",
        "company_size": "Enterprise",
        "lead_status": "Negotiation",
        "engagement_score": 90,
        "tech_stack_match": 95,
        "budget_score": 88,
        "website_visits": 18,
        "email_opens": 9,
        "meetings": 3
    }

    print(predict_lead(sample))
