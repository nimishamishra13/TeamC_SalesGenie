import time
import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from concurrent.futures import ThreadPoolExecutor
from modules.module2_intelligence import analyze_and_score_lead
from modules.module3_outreach import generate_outreach, OutreachRequest
from modules.module4_scoring import predict_lead, ScoreRequest
from modules.module5_conversation import (
    analyze_conversation,
    ConversationRequest,
    save_conversation,
    SaveConversationRequest
)

from database.connection import SessionLocal
from database.models import Lead

router = APIRouter(
    prefix="/pipeline",
    tags=["Milestone 4 - Integration"]
)


class PipelineRequest(BaseModel):

    lead_id: int

    transcript: str
def run_sales_pipeline(lead_id: int, transcript: str):

    pipeline_start = time.perf_counter()

    timing = {}

    # ============================================================
    # VALIDATE TRANSCRIPT
    # ============================================================

    if not transcript or not transcript.strip():

        raise ValueError(
            "A conversation transcript is required "
            "for the end-to-end pipeline."
        )

    db = SessionLocal()

    try:

        # ========================================================
        # 1. M1 — LEAD MANAGEMENT
        # ========================================================

        stage_start = time.perf_counter()

        lead = (
            db.query(Lead)
            .filter(Lead.id == lead_id)
            .first()
        )

        if not lead:

            raise ValueError(
                f"Lead {lead_id} not found"
            )

        lead_data = {

            "name": lead.contact,

            "company": lead.company,

            "industry": lead.industry,

            "status": lead.status,

            "designation": lead.designation or "",

            "website": lead.website or "",

            "location": lead.location or "",

            "notes": lead.notes or ""
        }

        timing["M1_lead_management"] = round(
            time.perf_counter() - stage_start,
            3
        )

        # ========================================================
        # 2. M2 — LEAD INTELLIGENCE
        # ========================================================

        stage_start = time.perf_counter()

        intelligence = analyze_and_score_lead(
            lead_data
        )

        timing["M2_lead_intelligence"] = round(
            time.perf_counter() - stage_start,
            3
        )

        analysis_json = json.dumps(
            intelligence,
            indent=2
        )

               # ========================================================
        # 3 & 4. M3 OUTREACH + M5 CONVERSATION
        # Execute independently in parallel
        # ========================================================

        parallel_start = time.perf_counter()

        if not transcript or not transcript.strip():
            raise ValueError(
                "A conversation transcript is required "
                "for the end-to-end pipeline."
            )

        def run_outreach():

            stage_start = time.perf_counter()

            outreach_request = OutreachRequest(
                name=lead.contact,
                company=lead.company,
                industry=lead.industry,
                status=lead.status,
                analysis=analysis_json,
                score=lead.score or 0
            )

            result = generate_outreach(
                outreach_request
            )

            elapsed = round(
                time.perf_counter() - stage_start,
                3
            )

            return result, elapsed


        def run_conversation():

            stage_start = time.perf_counter()

            conversation_request = ConversationRequest(
                lead_id=lead.id,
                transcript=transcript
            )

            result = analyze_conversation(
                conversation_request
            )

            elapsed = round(
                time.perf_counter() - stage_start,
                3
            )

            return result, elapsed


        with ThreadPoolExecutor(max_workers=2) as executor:

            outreach_future = executor.submit(
                run_outreach
            )

            conversation_future = executor.submit(
                run_conversation
            )

            outreach, outreach_time = (
                outreach_future.result()
            )

            conversation, conversation_time = (
                conversation_future.result()
            )


        timing["M3_outreach"] = outreach_time

        timing["M5_conversation_intelligence"] = (
            conversation_time
        )

        timing["M3_M5_parallel_execution"] = round(
            time.perf_counter() - parallel_start,
            3
        )

        # ========================================================
        # 5. CRM — SAVE CONVERSATION
        # ========================================================

        stage_start = time.perf_counter()

        save_request = SaveConversationRequest(

            lead_id=lead.id,

            transcript=transcript,

            summary=conversation["summary"],

            sentiment=conversation["sentiment"],

            buying_intent=conversation["buying_intent"],

            next_action="\n".join(
                conversation["next_actions"]
            ),

            crm_notes=conversation["crm_notes"]
        )

        crm_result = save_conversation(
            save_request
        )

        timing["CRM_sync"] = round(
            time.perf_counter() - stage_start,
            3
        )

        # ========================================================
        # 6. M4 — FINAL AI SCORING
        # ========================================================

        stage_start = time.perf_counter()

        score_request = ScoreRequest(

            lead_id=lead.id,

            name=lead.contact,

            company=lead.company,

            industry=lead.industry,

            status=lead.status,

            designation=lead.designation or "",

            website=lead.website or "",

            location=lead.location or "",

            notes=lead.notes or "",

            analysis=analysis_json
        )

        final_score = predict_lead(
            score_request,
            use_llm_recommendation=False
        ) 

        timing["M4_final_scoring"] = round(
            time.perf_counter() - stage_start,
            3
        )

        # ========================================================
        # 7. TOTAL PIPELINE TIME
        # ========================================================

        timing["TOTAL"] = round(
            time.perf_counter() - pipeline_start,
            3
        )

        # ========================================================
        # 8. RETURN COMPLETE PIPELINE RESULT
        # ========================================================

        return {

            "success": True,

            "lead_id": lead.id,

            "lead": {

                "company": lead.company,

                "contact": lead.contact,

                "status": lead.status,

                "deal_value": lead.deal_value or 0
            },

            "intelligence": intelligence,

            "outreach": outreach,

            "conversation": conversation,

            "crm": crm_result,

            "final_score": final_score,

            "timing": timing
        }

    finally:

        db.close()
@router.post("/run")
def run_pipeline(request: PipelineRequest):

    try:

        result = run_sales_pipeline(
            lead_id=request.lead_id,
            transcript=request.transcript
        )

        return result

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except Exception as e:

        print(
            "🔥 PIPELINE ERROR:",
            str(e)
        )

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
