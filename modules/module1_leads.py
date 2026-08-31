from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import json
import csv
import io

from fastapi import UploadFile, File

from modules.module2_intelligence import analyze_and_score_lead
from modules.module4_scoring import ScoreRequest, predict_lead

from database.connection import SessionLocal
from database.models import Lead, Conversation


router = APIRouter(
    prefix="/leads",
    tags=["Leads"]
)

# ==========================================================
# DATABASE DEPENDENCY
# ==========================================================

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@router.post("/import")
async def import_leads(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:
        # Read uploaded CSV
        contents = await file.read()

        decoded = contents.decode("utf-8-sig")

        reader = csv.DictReader(
            io.StringIO(decoded)
        )

        imported_count = 0

        for row in reader:

            lead = Lead(
                company=row.get("company", "").strip(),
                contact=row.get("contact", "").strip(),
                designation=row.get("designation", "").strip(),
                email=row.get("email", "").strip(),
                phone=row.get("phone", "").strip(),
                website=row.get("website", "").strip(),
                location=row.get("location", "").strip(),
                industry=row.get("industry", "").strip(),
                notes=row.get("notes", "").strip()
            )

            db.add(lead)
            imported_count += 1

        db.commit()

        return {
            "message": f"{imported_count} leads imported successfully",
            "count": imported_count
        }

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"CSV import failed: {str(e)}"
        )
# ==========================================================
# CREATE LEAD
# ==========================================================

@router.post("/")
def create_lead(
    data: dict,
    db: Session = Depends(get_db)
):

    # Module 2 performs initial AI analysis
    ai_result = analyze_and_score_lead(data)

    new_lead = Lead(
        company=data.get("company"),
        contact=data.get("contact"),
        designation=data.get("designation"),
        email=data.get("email"),
        phone=data.get("phone"),
        website=data.get("website"),
        location=data.get("location"),
        industry=data.get("industry"),

        # Initial values
        score=None,
        status=data.get("status", "New"),

        notes=data.get("notes")
    )

    db.add(new_lead)
    db.commit()
    db.refresh(new_lead)

    return {
        "message": "Lead created successfully",
        "lead": new_lead,
        "ai_analysis": ai_result
    }


# ==========================================================
# GET ALL LEADS
# ==========================================================

@router.get("/")
def get_leads(
    db: Session = Depends(get_db)
):

    return db.query(Lead).all()


# ==========================================================
# GET SINGLE LEAD
# ==========================================================

@router.get("/{lead_id}")
def get_lead(
    lead_id: int,
    db: Session = Depends(get_db)
):

    lead = (
        db.query(Lead)
        .filter(Lead.id == lead_id)
        .first()
    )

    if not lead:
        raise HTTPException(
            status_code=404,
            detail="Lead not found"
        )

    return lead


# ==========================================================
# UPDATE LEAD
# ==========================================================

@router.put("/{lead_id}")
def update_lead(
    lead_id: int,
    data: dict,
    db: Session = Depends(get_db)
):

    lead = (
        db.query(Lead)
        .filter(Lead.id == lead_id)
        .first()
    )

    if not lead:
        raise HTTPException(
            status_code=404,
            detail="Lead not found"
        )

    # ------------------------------------------------------
    # Update CRM information
    # ------------------------------------------------------

    lead.company = data.get(
        "company",
        lead.company
    )

    lead.contact = data.get(
        "contact",
        lead.contact
    )

    lead.designation = data.get(
        "designation",
        lead.designation
    )

    lead.email = data.get(
        "email",
        lead.email
    )

    lead.phone = data.get(
        "phone",
        lead.phone
    )

    lead.website = data.get(
        "website",
        lead.website
    )

    lead.location = data.get(
        "location",
        lead.location
    )
    lead.status = data.get(
        "status",
        lead.status
    )
    lead.industry = data.get(
        "industry",
        lead.industry
    )

    lead.notes = data.get(
        "notes",
        lead.notes
    )
    lead.deal_value = data.get(
        "deal_value",
        lead.deal_value
    )

    # ------------------------------------------------------
    # Re-run Module 2 AI analysis
    # ------------------------------------------------------

    ai = analyze_and_score_lead({
        "company": lead.company,
        "contact": lead.contact,
        "designation": lead.designation,
        "email": lead.email,
        "phone": lead.phone,
        "website": lead.website,
        "location": lead.location,
        "industry": lead.industry,
        "notes": lead.notes
    })

    db.commit()
    db.refresh(lead)

    return {
        "message": "Lead updated successfully",
        "lead": lead,
        "ai_analysis": ai
    }


# ==========================================================
# REANALYZE ALL LEADS
# ==========================================================
@router.post("/reanalyze")
def reanalyze_all_leads(
    db: Session = Depends(get_db)
):

    leads = db.query(Lead).all()

    results = []

    for lead in leads:

        try:

            # ---------------------------------------------
            # Latest conversation
            # ---------------------------------------------

            latest_conversation = (
                db.query(Conversation)
                .filter(
                    Conversation.lead_id == lead.id
                )
                .order_by(
                    Conversation.id.desc()
                )
                .first()
            )

            # ---------------------------------------------
            # Conversation analysis
            # ---------------------------------------------

            if latest_conversation:

                conversation_data = {

                    "sentiment":
                        latest_conversation.sentiment,

                    "buying_intent":
                        latest_conversation.buying_intent,

                    "objections": [],

                    "pain_points": [],

                    "next_actions":
                        [
                            latest_conversation.next_action
                        ]
                        if latest_conversation.next_action
                        else [],

                    "crm_notes":
                        latest_conversation.crm_notes or ""
                }

            else:

                conversation_data = {}

            # ---------------------------------------------
            # Build scoring request
            # ---------------------------------------------

            score_request = ScoreRequest(

                lead_id=lead.id,

                name=lead.contact or "",

                company=lead.company or "",

                industry=lead.industry or "",

                status=lead.status or "New",

                designation=lead.designation or "",

                website=lead.website or "",

                location=lead.location or "",

                notes=lead.notes or "",

                analysis=json.dumps(
                    conversation_data
                )
            )

            # ---------------------------------------------
            # AI scoring
            # ---------------------------------------------

            result = predict_lead(
                score_request
            )

            final_score = int(
                result["lead_score"]
            )

            final_ai_status = result.get(
                "lead_status",
                "Cold"
            )

            # ---------------------------------------------
            # Save AI results
            # ---------------------------------------------

            lead.score = final_score

            lead.ai_status = final_ai_status

            # IMPORTANT:
            # Do NOT change lead.status here.
            # status = sales pipeline stage
            # ai_status = Hot/Warm/Cold

            db.commit()

            results.append({

                "lead_id": lead.id,

                "company": lead.company,

                "score": final_score,

                "ai_status": final_ai_status,

                "status": lead.status

            })

            print(
                f"✅ {lead.company}: "
                f"{final_score} / "
                f"{final_ai_status}"
            )

        except Exception as e:

            db.rollback()

            print(
                f"❌ Failed to reanalyze "
                f"lead {lead.id}: {str(e)}"
            )

            results.append({

                "lead_id": lead.id,

                "company": lead.company,

                "error": str(e)

            })

    return {

        "message":
            f"{len(leads)} leads re-analyzed successfully.",

        "results": results

    }

# ==========================================================
# DELETE LEAD
# ==========================================================

@router.delete("/{lead_id}")
def delete_lead(
    lead_id: int,
    db: Session = Depends(get_db)
):

    lead = (
        db.query(Lead)
        .filter(Lead.id == lead_id)
        .first()
    )

    if not lead:
        raise HTTPException(
            status_code=404,
            detail="Lead not found"
        )

    db.delete(lead)
    db.commit()

    return {
        "message": "Lead deleted successfully"
    }
