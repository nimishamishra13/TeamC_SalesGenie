from fastapi import FastAPI
from database.connection import engine, Base
from database import models
from modules.auth import router as auth_router
# Module 1 (Leads)
from modules.module1_leads import router as leads_router

# Module 2 (Company Intelligence + Lead Scoring)
#from modules.module2_intelligence import router as intelligence_router

app = FastAPI()

# Create tables
Base.metadata.create_all(bind=engine)

# Include Module 1
app.include_router(leads_router)
app.include_router(auth_router)

# Include Module 2 (VERY IMPORTANT for fixing 404)
#app.include_router(intelligence_router)
