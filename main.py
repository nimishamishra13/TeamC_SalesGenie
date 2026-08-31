from fastapi import FastAPI
from database.connection import engine, Base
from database import models

# Module 1 (Leads)
from modules.module1_leads import router as leads_router
from modules.auth import router as auth_router

# Module 2 (Company Intelligence + Lead Scoring)

# Module 3 (AI Outreach Generation)
from modules.module3_outreach import router as outreach_router

# Module 4 (AI Lead Scoring + Recommendation)
from modules.module4_scoring import router as scoring_router
from modules.module4_recommendation import router as recommendation_router
from modules.module5_conversation import router as conversation_router
from modules.module6_dashboard import router as dashboard_router
# Milestone 4 — End-to-End Integration Pipeline
from modules.pipeline import router as pipeline_router
app = FastAPI()

# Create tables
Base.metadata.create_all(bind=engine)

# Include Module 1
app.include_router(leads_router)
app.include_router(auth_router)

# Include Module 2 

# Include Module 3 
app.include_router(outreach_router)

# Include Module 4 
app.include_router(scoring_router)
app.include_router(recommendation_router)
app.include_router(conversation_router)
app.include_router(dashboard_router)
app.include_router(pipeline_router)
