from ai.ai_analysis import analyze_lead
from ai.tech_stack import detect_tech_stack

def get_status(score):
    if score >= 90:
        return "Hot"
    elif score >= 75:
        return "Warm"
    return "Cold"


def analyze_and_score_lead(data: dict):
    combined_text = f"""
        {data.get('website')}
        {data.get('notes')}
        """

    tech_stack = detect_tech_stack(combined_text)
    prompt = f"""
        Company: {data.get('company')}
        Industry: {data.get('industry')}
        Location: {data.get('location')}
        Website: {data.get('website')}

        Detected Technology Stack:
        {", ".join(tech_stack) if tech_stack else "Not detected"}

        Primary Contact: {data.get('contact')}
        Designation: {data.get('designation')}

        Additional Notes:
        {data.get('notes')}

        Evaluate the lead according to the scoring criteria.
        """
    result = analyze_lead(prompt)
    
    return {
            "analysis": result,
            "score": result["lead_score"],
            "status": get_status(result["lead_score"])
        }
