from typing import Dict


def get_company_size(company: str) -> str:
    """
    Estimate company size based on company name.
    """

    enterprise = [
        "Infosys",
        "Microsoft",
        "Google",
        "Amazon",
        "NVIDIA",
        "IBM",
        "Oracle",
        "Accenture",
        "TCS",
        "Wipro"
    ]

    if company in enterprise:
        return "Enterprise"

    return "SMB"


def get_engagement_score(status: str) -> int:
    """
    Estimate engagement from lead status.
    """

    mapping = {
        "Hot": 90,
        "Warm": 70,
        "Cold": 40,
        "New": 20
    }

    return mapping.get(status, 50)


def get_budget_score(notes: str) -> int:
    """
    Estimate budget from notes.
    """

    notes = notes.lower()

    if "enterprise" in notes or "large budget" in notes:
        return 95

    if "budget" in notes:
        return 80

    return 60


def get_tech_stack_match(analysis: Dict) -> int:
    """
    Calculate tech stack compatibility.
    """

    tech_stack = analysis.get("tech_stack", [])

    score = len(tech_stack) * 20

    return min(score, 100)


def extract_features(lead, analysis):
    """
    Prepare ML features from CRM + AI Analysis.
    """

    return {

        "industry": lead["industry"],

        "company_size": get_company_size(
            lead["company"]
        ),

        "lead_status": {

            "Hot": "Negotiation",

            "Warm": "Qualified",

            "Cold": "Contacted",

            "New": "New"

        }.get(lead["status"], "New"),

        "engagement_score": get_engagement_score(
            lead["status"]
        ),

        "tech_stack_match": get_tech_stack_match(
            analysis
        ),

        "budget_score": get_budget_score(
            lead["notes"]
        ),

        "website_visits": 15,

        "email_opens": 7,

        "meetings": 2
    }
