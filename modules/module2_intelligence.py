from ai.ai_analysis import analyze_lead
from ai.tech_stack import detect_tech_stack


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

    result["tech_stack"] = tech_stack

    return result
