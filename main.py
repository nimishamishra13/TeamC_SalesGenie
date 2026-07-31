from fastapi import FastAPI

from database.connection import engine, Base
from database import models


# ==========================
# MODULE 1 : LEADS
# ==========================
from modules.module1_leads import router as leads_router


# ==========================
# MODULE 2 : INTELLIGENCE
# ==========================
from modules.module2_intelligence import router as intelligence_router


# ==========================
# MODULE 3 : AI OUTREACH
# ==========================
from modules.module3_outreach import router as outreach_router


# ==========================
# MODULE 4 : AI SCORING
# ==========================
from modules.module4_scoring import router as scoring_router


# ==========================
# MODULE 5 : CONVERSATION + CRM
# ==========================
from modules.module5_conversation import router as conversation_router


# ==========================
# MODULE 6 : DASHBOARD ANALYTICS
# ==========================
from modules.module6_dashboard import router as dashboard_router



app = FastAPI(
    title="SalesGenie AI",
    description="AI Powered Sales Intelligence Platform",
    version="1.0"
)



# ==========================
# CREATE DATABASE TABLES
# ==========================

Base.metadata.create_all(
    bind=engine
)



# ==========================
# REGISTER ALL MODULE ROUTERS
# ==========================


# Module 1
app.include_router(
    leads_router
)



# Module 2
app.include_router(
    intelligence_router
)



# Module 3
app.include_router(
    outreach_router
)



# Module 4
app.include_router(
    scoring_router
)



# Module 5
app.include_router(
    conversation_router
)



# Module 6
app.include_router(
    dashboard_router
)





# ==========================
# ROOT API
# ==========================

@app.get("/")
def home():

    return {

        "message":
        "SalesGenie AI Backend Running",

        "modules":
        [
            "Lead Management",
            "Company Intelligence",
            "AI Outreach Generation",
            "AI Lead Scoring",
            "Conversation Intelligence + CRM",
            "Dashboard Analytics"
        ]

    }
