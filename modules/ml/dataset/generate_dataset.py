import pandas as pd
import random

industries = [
    "Technology",
    "Finance",
    "Healthcare",
    "Education",
    "Retail",
    "Manufacturing",
    "IT Services",
    "Software",
    "Other"
]

company_sizes = [
    "Startup",
    "SMB",
    "Enterprise"
]

statuses = [
    "New",
    "Contacted",
    "Qualified",
    "Proposal Sent",
    "Negotiation"
]

rows = []

for _ in range(500):

    industry = random.choice(industries)
    company_size = random.choice(company_sizes)
    status = random.choice(statuses)

    engagement = random.randint(20, 100)
    tech_stack_match = random.randint(20, 100)
    budget_score = random.randint(20, 100)

    score = (
        engagement * 0.30 +
        tech_stack_match * 0.20 +
        budget_score * 0.20 
    )

    if status == "Negotiation":
        score += 20
    elif status == "Proposal Sent":
        score += 15
    elif status == "Qualified":
        score += 10
    elif status == "Contacted":
        score += 5

    if company_size == "Enterprise":
        score += 10
    elif company_size == "SMB":
        score += 5

    converted = 1 if score >= 85 else 0

    rows.append({
        "industry": industry,
        "company_size": company_size,
        "lead_status": status,
        "engagement_score": engagement,
        "tech_stack_match": tech_stack_match,
        "budget_score": budget_score,
        "converted": converted
    })

df = pd.DataFrame(rows)

df.to_csv("lead_dataset.csv", index=False)

print("Dataset created successfully!")
print(df.head())
