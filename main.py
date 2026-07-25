from fastapi import FastAPI
from database.connection import engine, Base
from database import models

# Module 1 (Leads)
from modules.module1_leads import router as leads_router

# Module 2 (Company Intelligence + Lead Scoring)
from modules.module2_intelligence import router as intelligence_router

# Module 3 (AI Outreach Generation)
from modules.module3_outreach import router as outreach_router

# Module 4 (AI Lead Scoring + Recommendation)
from modules.module4_scoring import router as scoring_router


app = FastAPI()

# Create tables
Base.metadata.create_all(bind=engine)

# Include Module 1
app.include_router(leads_router)

# Include Module 2 
app.include_router(intelligence_router)

# Include Module 3 
app.include_router(outreach_router)

# Include Module 4 
app.include_router(scoring_router)
