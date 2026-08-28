from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import timedelta

from database.connection import get_db
from database.models import (
    Lead,
    Conversation,
    CRMActivity,
    OutreachHistory,
)

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard Analytics"],
)


# ==========================================================
# DEMO / PIPELINE INITIALIZATION
# ==========================================================

@router.post("/initialize-demo-data")
def initialize_demo_data(
    db: Session = Depends(get_db),
):
    """
    Initializes realistic CRM pipeline data for the demo.

    IMPORTANT:
    - Lead.status = CRM pipeline stage
    - Lead.score = AI score
    - Lead.ai_status = AI classification (Hot/Warm/Cold)
    - Lead.deal_value = estimated deal value
    """

    pipeline_data = {
        1: ("Won", 2000000),
        2: ("Contacted", 500000),
        3: ("Proposal Sent", 1500000),
        4: ("Qualified", 800000),
        5: ("Qualified", 600000),
        6: ("Contacted", 750000),
        7: ("Negotiation", 650000),
        8: ("Contacted", 400000),
        9: ("Qualified", 1200000),
        10: ("Contacted", 900000),
        11: ("Proposal Sent", 1000000),
        12: ("Won", 800000),
        13: ("Contacted", 500000),
        14: ("Lost", 700000),
        15: ("Contacted", 350000),
        16: ("Negotiation", 900000),
        17: ("Proposal Sent", 600000),
        18: ("Lost", 450000),
        19: ("Proposal Sent", 1400000),
        20: ("New", 550000),
        21: ("Qualified", 1100000),
    }

    # Different cycle lengths make the sales-cycle KPI meaningful.
    closed_days = {
        1: 18,
        12: 14,
        14: 11,
        18: 21,
    }

    updated = 0

    for lead_id, (status, deal_value) in pipeline_data.items():

        lead = (
            db.query(Lead)
            .filter(Lead.id == lead_id)
            .first()
        )

        if lead:
            lead.status = status
            lead.deal_value = deal_value

            if status in ["Won", "Lost"] and lead.created_at:
                lead.closed_at = (
                    lead.created_at
                    + timedelta(days=closed_days.get(lead_id, 14))
                )
            else:
                lead.closed_at = None

            updated += 1

    db.commit()

    return {
        "message": "Demo pipeline data initialized",
        "updated_leads": updated,
    }


# ==========================================================
# SALES SUMMARY / KPI DASHBOARD
# ==========================================================

@router.get("/summary")
def dashboard_summary(
    db: Session = Depends(get_db),
):
    total_leads = db.query(Lead).count()

    won_leads = (
        db.query(Lead)
        .filter(func.lower(Lead.status) == "won")
        .count()
    )

    conversion_rate = (
        round((won_leads / total_leads) * 100, 2)
        if total_leads > 0
        else 0
    )

    # Active pipeline excludes Won and Lost deals.
    pipeline_value = (
        db.query(func.sum(Lead.deal_value))
        .filter(
            ~func.lower(Lead.status).in_(["won", "lost"])
        )
        .scalar()
        or 0
    )

    scores = [
        lead.score
        for lead in db.query(Lead).all()
        if lead.score is not None
    ]

    average_ai_score = (
        round(sum(scores) / len(scores), 2)
        if scores
        else 0
    )

    high_quality_leads = (
        db.query(Lead)
        .filter(Lead.score >= 75)
        .count()
    )

    closed_leads = (
        db.query(Lead)
        .filter(Lead.closed_at.isnot(None))
        .all()
    )

    sales_cycles = []

    for lead in closed_leads:
        if lead.created_at and lead.closed_at:
            days = (
                lead.closed_at - lead.created_at
            ).days
            sales_cycles.append(days)

    average_sales_cycle = (
        round(
            sum(sales_cycles) / len(sales_cycles),
            1,
        )
        if sales_cycles
        else 0
    )

    return {
        "total_leads": total_leads,
        "won_leads": won_leads,
        "conversion_rate": conversion_rate,
        "pipeline_value": pipeline_value,
        "average_sales_cycle": average_sales_cycle,
        "average_ai_score": average_ai_score,
        "high_quality_leads": high_quality_leads,
    }


# ==========================================================
# PIPELINE COUNTS
# ==========================================================

@router.get("/pipeline")
def pipeline_status(
    db: Session = Depends(get_db),
):
    result = (
        db.query(
            Lead.status,
            func.count(Lead.id),
        )
        .group_by(Lead.status)
        .all()
    )

    pipeline = {}

    for status, count in result:
        pipeline[status or "Unknown"] = count

    return {
        "pipeline": pipeline,
    }


# ==========================================================
# PIPELINE VALUE
# ==========================================================

@router.get("/pipeline-value")
def pipeline_value(
    db: Session = Depends(get_db),
):
    active_statuses = [
        "new",
        "contacted",
        "qualified",
        "proposal sent",
        "negotiation",
    ]

    leads = db.query(Lead).all()

    total_value = 0

    for lead in leads:
        status = (
            (lead.status or "")
            .lower()
            .strip()
        )

        if status in active_statuses:
            total_value += lead.deal_value or 0

    return {
        "pipeline_value": total_value,
    }


# ==========================================================
# SALES CYCLE
# ==========================================================

@router.get("/sales-cycle")
def sales_cycle(
    db: Session = Depends(get_db),
):
    closed_leads = (
        db.query(Lead)
        .filter(Lead.closed_at.isnot(None))
        .all()
    )

    cycles = []

    for lead in closed_leads:
        if lead.created_at and lead.closed_at:
            days = (
                lead.closed_at - lead.created_at
            ).days
            cycles.append(days)

    average = (
        round(sum(cycles) / len(cycles), 2)
        if cycles
        else 0
    )

    return {
        "average_sales_cycle_days": average,
        "closed_leads_analyzed": len(cycles),
    }


# ==========================================================
# OUTREACH PERFORMANCE
# ==========================================================

@router.get("/outreach")
def outreach_performance(
    db: Session = Depends(get_db),
):
    total_outreach = (
        db.query(OutreachHistory).count()
    )

    return {
        "total_outreach_generated": total_outreach,
    }


# ==========================================================
# AI SCORE INSIGHTS
# ==========================================================

@router.get("/scores")
def score_insights(
    db: Session = Depends(get_db),
):
    average_score = (
        db.query(func.avg(Lead.score))
        .scalar()
    )

    high_quality = (
        db.query(Lead)
        .filter(Lead.score >= 75)
        .count()
    )

    return {
        "average_score": (
            round(float(average_score), 2)
            if average_score is not None
            else 0
        ),
        "high_quality_leads": high_quality,
    }


# ==========================================================
# CRM ACTIVITY REPORT
# ==========================================================

@router.get("/crm")
def crm_report(
    db: Session = Depends(get_db),
):
    activities = (
        db.query(CRMActivity).count()
    )

    conversations = (
        db.query(Conversation).count()
    )

    return {
        "crm_activities": activities,
        "customer_conversations": conversations,
    }


# ==========================================================
# SALES INTELLIGENCE REPORT
# ==========================================================

@router.get("/report")
def sales_report(
    db: Session = Depends(get_db),
):
    total_leads = db.query(Lead).count()

    won = (
        db.query(Lead)
        .filter(func.lower(Lead.status) == "won")
        .count()
    )

    high_priority = (
        db.query(Lead)
        .filter(Lead.score >= 75)
        .count()
    )

    return {
        "sales_summary": {
            "total_leads": total_leads,
            "won_leads": won,
            "high_priority_leads": high_priority,
        },
        "recommendation": (
            "Focus follow-ups on high-scoring active leads."
        ),
    }


# ==========================================================
# AI FOLLOW-UP RECOMMENDATIONS
# ==========================================================

@router.get("/recommendations")
def follow_up_recommendations(
    db: Session = Depends(get_db),
):
    leads = db.query(Lead).all()

    recommendations = []

    for lead in leads:

        score = lead.score or 0

        pipeline_status = (
            lead.status or "New"
        ).strip()

        status = pipeline_status.lower()

        ai_status = (
            lead.ai_status or "Cold"
        )

        # -----------------------------------------------
        # WON
        # -----------------------------------------------

        if status == "won":

            action = (
                "Prepare onboarding and maintain "
                "customer relationship"
            )

            priority = "Low"

        # -----------------------------------------------
        # LOST
        # -----------------------------------------------

        elif status == "lost":

            action = (
                "Review loss reason and consider "
                "future re-engagement"
            )

            priority = "Low"

        # -----------------------------------------------
        # NEGOTIATION + HIGH AI SCORE
        # -----------------------------------------------

        elif (
            status == "negotiation"
            and score >= 75
        ):

            action = (
                "Schedule decision-maker follow-up "
                "within 24 hours"
            )

            priority = "High"

        # -----------------------------------------------
        # PROPOSAL SENT
        # -----------------------------------------------

        elif (
            status == "proposal sent"
            and score >= 50
        ):

            action = (
                "Follow up on proposal and "
                "address objections"
            )

            priority = "High"

        # -----------------------------------------------
        # QUALIFIED
        # -----------------------------------------------

        elif status == "qualified":

            action = (
                "Schedule a discovery/demo meeting"
            )

            priority = (
                "High"
                if score >= 75
                else "Medium"
            )

        # -----------------------------------------------
        # CONTACTED
        # -----------------------------------------------

        elif status == "contacted":

            action = (
                "Send a personalized follow-up "
                "within 48 hours"
            )

            priority = (
                "High"
                if score >= 75
                else "Medium"
            )

        # -----------------------------------------------
        # NEW
        # -----------------------------------------------

        else:

            action = (
                "Perform initial outreach and "
                "qualify the lead"
            )

            priority = (
                "Medium"
                if score >= 50
                else "Low"
            )

        recommendations.append({
            "lead_id": lead.id,
            "company": lead.company,
            "status": pipeline_status,
            "score": score,
            "ai_status": ai_status,
            "deal_value": lead.deal_value or 0,
            "recommended_action": action,
            "priority": priority,
        })

    priority_order = {
        "High": 0,
        "Medium": 1,
        "Low": 2,
    }

    recommendations.sort(
        key=lambda x: (
            priority_order.get(
                x["priority"],
                3,
            ),
            -x["score"],
        )
    )

    return {
        "total_recommendations": len(
            recommendations
        ),
        "recommendations": recommendations,
    }


# ==========================================================
# KANBAN PIPELINE
# ==========================================================

@router.get("/kanban")
def kanban_pipeline(
    db: Session = Depends(get_db),
):
    statuses = [
        "New",
        "Contacted",
        "Qualified",
        "Proposal Sent",
        "Negotiation",
        "Won",
        "Lost",
    ]

    pipeline = {
        status: []
        for status in statuses
    }

    leads = db.query(Lead).all()

    for lead in leads:

        status = (
            lead.status or "New"
        ).strip()

        if status not in pipeline:
            status = "New"

        pipeline[status].append({
            "id": lead.id,
            "company": lead.company,
            "contact": lead.contact,
            "designation": lead.designation,
            "score": lead.score or 0,
            "ai_status": (
                lead.ai_status or "Cold"
            ),
            "deal_value": (
                lead.deal_value or 0
            ),
            "notes": lead.notes or "",
        })

    return {
        "pipeline": pipeline,
    }
