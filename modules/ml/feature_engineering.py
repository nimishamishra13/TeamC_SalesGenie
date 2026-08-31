from typing import Dict

from ai.tech_stack import detect_tech_stack


# ==========================================================
# COMPANY SIZE
# ==========================================================

def get_company_size(company: str) -> str:
    """
    Determine company size from known enterprise companies.
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

    company = (company or "").strip().lower()

    if company in [name.lower() for name in enterprise]:
        return "Enterprise"

    return "SMB"


# ==========================================================
# DECISION MAKER SCORE
# ==========================================================

def get_decision_maker_score(designation: str) -> int:
    """
    Score the authority of the contact person.

    Maximum: 15
    """

    designation = (designation or "").lower().strip()

    # C-level / founders / owners
    if any(role in designation for role in [
        "ceo",
        "cto",
        "cio",
        "cfo",
        "coo",
        "founder",
        "owner",
        "president"
    ]):
        return 15

    # Senior leadership
    if any(role in designation for role in [
        "vp",
        "vice president",
        "director"
    ]):
        return 12

    # Management
    if "manager" in designation:
        return 8

    # Executive
    if "executive" in designation:
        return 5

    return 3


# ==========================================================
# BUDGET SCORE
# ==========================================================

def get_budget_score(notes: str) -> int:
    """
    Estimate budget strength from CRM notes.

    Score is normalized to 0-100.
    """

    notes = (notes or "").lower()

    if "large budget" in notes:
        return 100

    if "enterprise budget" in notes:
        return 95

    if "enterprise" in notes:
        return 90

    if "budget" in notes:
        return 75

    return 60


# ==========================================================
# TECHNOLOGY STACK MATCH
# ==========================================================

def get_tech_stack_match(
    lead,
    analysis: Dict
) -> int:
    """
    Calculate technology compatibility.

    Uses:
    - Website
    - CRM notes
    - AI analysis
    """

    text = f"""
    {lead.get("website", "")}
    {lead.get("notes", "")}
    {analysis.get("tech_stack", "")}
    """

    tech_stack = detect_tech_stack(text)

    print(
        "🔥 TECH STACK USED FOR SCORING:",
        tech_stack
    )

    weights = {

        # AI / ML
        "Artificial Intelligence": 20,
        "Machine Learning": 20,
        "Deep Learning": 20,
        "Generative AI": 20,

        "PyTorch": 18,
        "TensorFlow": 18,
        "CUDA": 18,

        # Cloud
        "AWS": 15,
        "Azure": 15,
        "GCP": 15,

        # Infrastructure
        "Kubernetes": 15,
        "Docker": 12,

        # Programming
        "Python": 10,
        "Java": 10,
        "Node.js": 8,

        # Frontend
        "React": 7,
        "Angular": 7,
        "Vue": 7,

        # Databases
        "PostgreSQL": 7,
        "MongoDB": 7,
        "MySQL": 5,
        "Redis": 5,

        # Data engineering
        "Apache Spark": 10,
        "Hadoop": 8,
        "Databricks": 10
    }

    score = sum(
        weights.get(tech, 5)
        for tech in tech_stack
    )

    return min(score, 100)


# ==========================================================
# FEATURE ENGINEERING
# ==========================================================

def extract_features(
    lead,
    analysis
):
    """
    Prepare lead features for AI lead scoring.

    IMPORTANT:
    CRM status is NOT used to calculate engagement.

    Hot / Warm / Cold is determined AFTER
    the final AI lead score is calculated.
    """

    analysis = analysis or {}

    company = lead.get("company", "")
    industry = lead.get("industry", "")
    notes = lead.get("notes", "")
    designation = lead.get("designation", "")

    # ------------------------------------------------------
    # Calculate profile features
    # ------------------------------------------------------

    company_size = get_company_size(company)

    decision_maker_score = get_decision_maker_score(
        designation
    )

    budget_score = get_budget_score(notes)

    tech_stack_match = get_tech_stack_match(
        lead,
        analysis
    )

    print(
        "🔥 DESIGNATION RECEIVED:",
        repr(designation)
    )

    print(
        "🔥 DECISION MAKER SCORE:",
        decision_maker_score
    )

    # ------------------------------------------------------
    # Return features
    #
    # Notice:
    # NO lead status
    # NO status-based engagement
    # ------------------------------------------------------

    features = {

        "industry": industry,

        "company_size": company_size,

        "decision_maker_score": decision_maker_score,

        "tech_stack_match": tech_stack_match,

        "budget_score": budget_score
    }

    return features
