from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from database.connection import get_db
from database.models import (
    Lead,
    Conversation,
    CRMActivity,
    OutreachHistory,
    LeadScore
)


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard Analytics"]
)



# ======================================
# SALES SUMMARY
# ======================================

@router.get("/summary")
def dashboard_summary(
    db: Session = Depends(get_db)
):

    total_leads = db.query(
        Lead
    ).count()


    converted_leads = db.query(
        Lead
    ).filter(
        Lead.status == "converted"
    ).count()


    contacted_leads = db.query(
        Lead
    ).filter(
        Lead.status == "contacted"
    ).count()


    new_leads = db.query(
        Lead
    ).filter(
        Lead.status == "new"
    ).count()



    conversion_rate = 0

    if total_leads > 0:

        conversion_rate = round(
            (converted_leads / total_leads) * 100,
            2
        )



    return {

        "total_leads": total_leads,

        "new_leads": new_leads,

        "contacted_leads": contacted_leads,

        "converted_leads": converted_leads,

        "conversion_rate": f"{conversion_rate}%"

    }





# ======================================
# PIPELINE STATUS
# ======================================

@router.get("/pipeline")
def pipeline_status(
    db: Session = Depends(get_db)
):


    result = db.query(
        Lead.status,
        func.count(Lead.id)
    ).group_by(
        Lead.status
    ).all()



    pipeline = {}


    for status,count in result:

        pipeline[status] = count



    return {

        "pipeline": pipeline

    }





# ======================================
# OUTREACH PERFORMANCE
# ======================================

@router.get("/outreach")
def outreach_performance(
    db: Session = Depends(get_db)
):


    total_outreach = db.query(
        OutreachHistory
    ).count()



    return {

        "total_outreach_generated":
        total_outreach

    }





# ======================================
# AI SCORE INSIGHTS
# ======================================

@router.get("/scores")
def score_insights(
    db: Session = Depends(get_db)
):


    average_score = db.query(
        func.avg(
            LeadScore.score
        )
    ).scalar()



    high_quality = db.query(
        LeadScore
    ).filter(
        LeadScore.score >= 80
    ).count()



    return {


        "average_score":
        round(average_score,2)
        if average_score
        else 0,


        "high_quality_leads":
        high_quality

    }





# ======================================
# CRM ACTIVITY REPORT
# ======================================

@router.get("/crm")
def crm_report(
    db: Session = Depends(get_db)
):


    activities = db.query(
        CRMActivity
    ).count()



    conversations = db.query(
        Conversation
    ).count()



    return {

        "crm_activities":
        activities,


        "customer_conversations":
        conversations

    }





# ======================================
# SALES INTELLIGENCE REPORT
# ======================================

@router.get("/report")
def sales_report(
    db: Session = Depends(get_db)
):


    total_leads = db.query(
        Lead
    ).count()


    converted = db.query(
        Lead
    ).filter(
        Lead.status=="converted"
    ).count()



    best_scores = db.query(
        LeadScore
    ).filter(
        LeadScore.score >= 80
    ).count()



    return {


        "sales_summary":

        {

            "total_leads":
            total_leads,


            "converted_leads":
            converted,


            "high_priority_leads":
            best_scores

        },


        "recommendation":

        "Focus follow-ups on high scoring leads and contacted customers."

    }

from typing import cast

@router.get("/recommendations")
def follow_up_recommendations(db: Session = Depends(get_db)):

    leads = db.query(Lead).all()
    recommendations = []

    for lead in leads:

        score = 0

        lead_score = (
            db.query(LeadScore)
            .filter(LeadScore.lead_id == lead.id)
            .first()
        )

        # ✅ FIXED
        if lead_score is not None and lead_score.score is not None:
            score = cast(int, lead_score.score)

        status = lead.status if lead.status is not None else ""
        status = status.lower()

        if status == "converted":
            action = "Prepare onboarding and maintain customer relationship"
            priority = "Low"

        elif score >= 80:
            action = "Schedule sales meeting within 24 hours"
            priority = "High"

        elif score >= 50:
            action = "Send personalized follow-up email"
            priority = "Medium"

        else:
            action = "Perform cold outreach"
            priority = "Low"

        recommendations.append({
            "lead_id": lead.id,
            "company": lead.company,
            "status": status,
            "score": score,
            "recommended_action": action,
            "priority": priority
        })

    return {
        "total_recommendations": len(recommendations),
        "recommendations": recommendations
    }
