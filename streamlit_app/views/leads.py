import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os
import json
import csv
import io

from fastapi import UploadFile, File
sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..")
    )
)
from ai.ai_analysis import analyze_lead, build_lead_analysis
from views.ai_panel import show_ai_analysis
# ==========================================================
# SAMPLE DATA
# ==========================================================

import requests

try:
    response = requests.get("http://127.0.0.1:8000/leads/")
    response.raise_for_status()
    prospects = response.json()
except Exception as e:
    st.error(f"Unable to connect to backend: {e}")
    prospects = []



# ==========================================================
# STATUS BADGES
# ==========================================================

def status_badge(status):

    colors = {
        "Hot":"#EF4444",
        "Warm":"#F59E0B",
        "Cold":"#9CA3AF",
        "New":"#2563EB"
    }

    color = colors.get(status,"#6B7280")

    st.markdown(
        f"""
        <div style="
            display:inline-block;
            padding:6px 16px;
            border-radius:25px;
            background:{color};
            color:white;
            font-weight:600;
            font-size:13px;
            text-align:center;">
            {status}
        </div>
        """,
        unsafe_allow_html=True
    )


# ==========================================================
# KPI DASHBOARD
# ==========================================================

# KPI DASHBOARD
# ==========================================================

def dashboard_cards(prospects):

    total = len(prospects)

    # Make sure session state exists
    if "lead_scores" not in st.session_state:
        st.session_state.lead_scores = {}

    # Get only leads that have an AI score
    scored_leads = [
        p for p in prospects
        if p["id"] in st.session_state.lead_scores
    ]

    # Calculate AI status from AI score
    hot = 0
    warm = 0

    for p in scored_leads:

        score = st.session_state.lead_scores[p["id"]]["lead_score"]

        if score >= 90:
            hot += 1

        elif score >= 75:
            warm += 1

    # Average AI score
    ai_scores = [
        st.session_state.lead_scores[p["id"]]["lead_score"]
        for p in scored_leads
    ]

    avg = (
        int(sum(ai_scores) / len(ai_scores))
        if ai_scores
        else 0
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric(
            "📈 Total Leads",
            total
        )

    with c2:
        st.metric(
            "🔥 Hot Leads",
            hot
        )

    with c3:
        st.metric(
            "🟡 Warm Leads",
            warm
        )

    with c4:
        st.metric(
            "⭐ Avg AI Score",
            f"{avg}/100"
        )
# ==========================================================
# CHARTS
# ==========================================================

def show_charts(prospects):

    left,right = st.columns(2)

    status_df = pd.DataFrame({

        "Status":[
            "Hot",
            "Warm",
            "Cold",
            "New"
        ],

        "Count":[

            len([p for p in prospects if p["status"]=="Hot"]),

            len([p for p in prospects if p["status"]=="Warm"]),

            len([p for p in prospects if p["status"]=="Cold"]),

            len([p for p in prospects if p["status"]=="New"])

        ]

    })

    with left:

        fig = px.pie(

            status_df,

            values="Count",

            names="Status",

            hole=.55,

            title="Lead Status Distribution",

            color="Status",

            color_discrete_map={

                "Hot":"#EF4444",

                "Warm":"#F59E0B",

                "Cold":"#9CA3AF",

                "New":"#2563EB"

            }

        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    industry = {}

    for p in prospects:

        industry[p["industry"]] = industry.get(
            p["industry"],
            0
        ) + 1

    industry_df = pd.DataFrame({

        "Industry":list(industry.keys()),

        "Count":list(industry.values())

    })

    with right:

        fig = px.bar(

            industry_df,

            x="Industry",

            y="Count",

            title="Leads by Industry",

            color="Industry"

        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )
@st.dialog("✏️ Edit Prospect")
def edit_prospect_dialog(p):

    # ============================================================
    # BASIC PROSPECT INFORMATION
    # ============================================================

    col1, col2 = st.columns(2)

    with col1:

        company = st.text_input(
            "🏢 Company",
            value=p.get("company", "")
        )

        industry = st.selectbox(
            "🏭 Industry",
            [
                "Technology",
                "Finance",
                "Healthcare",
                "Education",
                "Retail",
                "Manufacturing",
                "IT Services",
                "Software",
                "Other"
            ],
            index=(
                [
                    "Technology",
                    "Finance",
                    "Healthcare",
                    "Education",
                    "Retail",
                    "Manufacturing",
                    "IT Services",
                    "Software",
                    "Other"
                ].index(p.get("industry"))
                if p.get("industry") in [
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
                else 0
            )
        )

        location = st.text_input(
            "📍 Location",
            value=p.get("location", "")
        )

        website = st.text_input(
            "🌐 Website",
            value=p.get("website", "")
        )

    with col2:

        contact = st.text_input(
            "👤 Contact",
            value=p.get("contact", "")
        )

        designation = st.text_input(
            "💼 Designation",
            value=p.get("designation", "")
        )

        email = st.text_input(
            "📧 Email",
            value=p.get("email", "")
        )

        phone = st.text_input(
            "📞 Phone",
            value=p.get("phone", "")
        )

    # ============================================================
    # SALES / PIPELINE INFORMATION
    # ============================================================

    st.markdown("### 💼 Sales & Pipeline Information")

    pipeline_col1, pipeline_col2 = st.columns(2)

    with pipeline_col1:

        deal_value = st.number_input(
            "💰 Pipeline Value",
            min_value=0.0,
            value=float(p.get("deal_value") or 0),
            step=1000.0,
            help="Estimated value of the potential deal."
        )

    with pipeline_col2:

        pipeline_statuses = [
            "New",
            "Qualified",
            "Contacted",
            "Proposal",
            "Negotiation",
            "Won",
            "Lost"
        ]

        current_status = p.get("status", "New")

        if current_status not in pipeline_statuses:
            current_status = "New"

        pipeline_status = st.selectbox(
            "📊 Pipeline Status",
            pipeline_statuses,
            index=pipeline_statuses.index(current_status)
        )

    # ============================================================
    # NOTES
    # ============================================================

    notes = st.text_area(
        "📝 Notes",
        value=p.get("notes", ""),
        height=120
    )

    # ============================================================
    # ACTION BUTTONS
    # ============================================================

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "💾 Save Changes",
            use_container_width=True
        ):

            response = requests.put(
                f"http://127.0.0.1:8000/leads/{p['id']}",
                json={
                    "company": company,
                    "contact": contact,
                    "designation": designation,
                    "email": email,
                    "phone": phone,
                    "website": website,
                    "location": location,
                    "industry": industry,
                    "notes": notes,

                    # Sales / Pipeline fields
                    "deal_value": deal_value,
                    "status": pipeline_status
                }
            )

            print("🔥 EDIT PROSPECT RESPONSE:")
            print(response.status_code)
            print(response.text)

            if response.status_code == 200:

                st.success(
                    "✅ Lead updated successfully!"
                )

                requests.post(
                    "http://127.0.0.1:8000/activity/add",
                    json={
                        "lead_id": p["id"],
                        "activity": "Lead details updated"
                    }
                )

                # Clear cached prospect data
                st.session_state.pop(
                    "prospects",
                    None
                )

                st.rerun()

            else:

                st.error(
                    f"Update failed.\n\n"
                    f"{response.text}"
                )

    with col2:

        if st.button(
            "❌ Cancel",
            use_container_width=True
        ):

            st.rerun()
# ==========================================================
# MAIN PAGE
# ==========================================================

def show_leads():
    try:
        response = requests.get("http://127.0.0.1:8000/leads/")
        response.raise_for_status()
        prospects = response.json()
    except Exception as e:
        st.error(f"Backend not running: {e}")
        prospects = [] 
    if "outreach_emails" not in st.session_state:
        st.session_state.outreach_emails = {}
    if "lead_scores" not in st.session_state:
        st.session_state.lead_scores = {}
    if "activities" not in st.session_state:
        st.session_state.activities = {}
       # ==========================================================
# PROSPECT DETAILS PAGE
# ==========================================================

    if "selected_prospect" in st.session_state:

        p = st.session_state.selected_prospect

        if st.button("⬅ Back to Leads"):
            del st.session_state.selected_prospect
            st.rerun()

        st.title(f"🏢 {p['company']}")

        st.caption(
            f"{p['industry']} • {p['location']}"
        )

        c1, c2, c3 = st.columns([1.2,1,1])

        with c1:

            ai_score = None

            if "lead_scores" in st.session_state:
                ai_score = p.get("score")

            if ai_score is not None:

                st.metric(
                    "⭐ AI Lead Score",
                    f"{ai_score}/100"
                )

                st.progress(ai_score / 100)

            else:

                st.metric(
                    "⭐ AI Lead Score",
                    "Not calculated"
                )


        with c2:

            if ai_score is None:
                ai_status = "Not Scored"
            elif ai_score >= 75:
                ai_status = "Hot"
            elif ai_score >= 50:
                ai_status = "Warm"
            else:
                ai_status = "Cold"

            st.metric(
                "AI Status",
                ai_status
            )
            
        with c3:

            if ai_score is None:
                priority = "Not calculated"
            elif ai_score >= 75:
                priority = "High"
            elif ai_score >= 50:
                priority = "Medium"
            else:
                priority = "Low"

            st.metric(
                "Priority",
                priority
            )

        st.divider()

        overview, ai, outreach, scoring, conversation,activity, notes = st.tabs(

            [

                "🏢 Overview",
                "🤖 AI Insights",
                "📧 AI Outreach",
                "🎯 AI Lead Score",
                "💬 Conversation Intelligence",
                "📅 Activity",
                "📝 Notes"

            ]

        )

        # ======================================================

        with overview:

            left, right = st.columns(2)

            with left:

                st.markdown("### Company Information")

                st.write("**🌐 Website**")
                st.write(p["website"])

                st.write("")

                st.write("**📍 Location**")
                st.write(p["location"])

                st.write("")

                st.write("**🏭 Industry**")
                st.write(p["industry"])

            with right:

                st.markdown("### Contact Information")

                st.write("**👤 Contact**")
                st.write(p["contact"])

                st.write("")

                st.write("**💼 Designation**")
                st.write(p["designation"])

                st.write("")

                st.write("**📧 Email**")
                st.write(p["email"])

                st.write("")

                st.write("**📞 Phone**")
                st.write(p["phone"])
            
        # ======================================================

        with ai:
            show_ai_analysis(p)
            
        # ======================================================
        with outreach:

            st.subheader("📧 AI Outreach")

            lead_id = p["id"]

            if lead_id not in st.session_state.outreach_emails:

                st.info("Generate a personalized outreach email for this lead.")

                if st.button(
                    "🚀 Generate Outreach Email",
                    key=f"generate_{lead_id}",
                    type="primary",
                    use_container_width=True,
                ):

                    with st.spinner("🔍 Analyzing lead..."):
                        analysis = build_lead_analysis(p)

                    with st.spinner("✍️ Generating personalized email..."):

                        response = requests.post(
                            "http://127.0.0.1:8000/outreach/generate",
                            json={
                                "name": p["contact"],
                                "company": p["company"],
                                "industry": p["industry"],
                                "status": p["status"],
                                "analysis": json.dumps(analysis, indent=2),
                            },
                        )
                        print("🔥 OUTREACH STATUS:", response.status_code)
                        print("🔥 OUTREACH RESPONSE:", response.text)

                    if response.status_code == 200:

                        st.session_state.outreach_emails[lead_id] = {
                            "email": response.json(),
                            "analysis": analysis,
                        }
                        if lead_id not in st.session_state.activities:
                            st.session_state.activities[lead_id] = []

                        activity = {
                            "icon": "📧",
                            "title": "Personalized Outreach Generated"
                        }

                        if activity not in st.session_state.activities[lead_id]:
                            st.session_state.activities[lead_id].append(activity)
                        st.rerun()

                    else:
                        st.error("Unable to generate outreach email.")

            else:

                data = st.session_state.outreach_emails[lead_id]

                email = data["email"]
                analysis = data["analysis"]
                st.subheader("🎯 Recommended Tone")
                st.info(email["tone"])
                st.subheader("📧 Subject")
                st.info(email["subject"])
                edited_email = st.text_area(
                    "✉️ Personalized Email",
                    value=email["message"],
                    height=320,
                    key=f"email_editor_{lead_id}"
                )
                save_col, regen_col = st.columns(2)

                with save_col:

                    if st.button(
                        "💾 Save Changes",
                        key=f"save_{lead_id}",
                        use_container_width=True,
                    ):

                        st.session_state.outreach_emails[lead_id]["email"]["message"] = edited_email

                        st.success("Email updated successfully!")
                with regen_col:

                    if st.button(
                        "🔄 Regenerate Email",
                        key=f"regen_{lead_id}",
                        use_container_width=True,
                    ):
                        with st.spinner("Generating a fresh version..."):
                        
                            response = requests.post(
                                "http://127.0.0.1:8000/outreach/generate",
                                json={
                                    "name": p["contact"],
                                    "company": p["company"],
                                    "industry": p["industry"],
                                    "status": p["status"],
                                    "analysis": json.dumps(analysis, indent=2),
                                },
                            )
                            print("🔥 OUTREACH STATUS:", response.status_code)
                            print("🔥 OUTREACH RESPONSE:", response.text)
                        
                        if response.status_code == 200:
                        
                            st.session_state.outreach_emails[lead_id]["email"] = response.json()
                                                
                            st.rerun()

                


        with scoring:

            st.subheader("🎯 AI Lead Scoring")

            lead_id = p["id"]

            if p.get("score") is None:

                st.info("Generate an AI-powered lead score and recommendations.")

                if st.button(
                    "🚀 Predict Lead Score",
                    key=f"score_{lead_id}",
                    type="primary",
                    use_container_width=True,
                ):
                    with st.spinner("🤖 AI is evaluating this lead..."):

                        analysis = build_lead_analysis(p)

                        response = requests.post(
                            "http://127.0.0.1:8000/score/predict",
                            json={
                                "lead_id": p["id"],
                                "name": p["contact"],
                                "company": p["company"],
                                "industry": p["industry"],
                                "designation": p["designation"],
                                "website": p["website"],
                                "status": p["status"],
                                "notes": p["notes"],
                                "analysis": json.dumps(analysis, indent=2)
                            }
                        )

                    if response.status_code == 200:
                        print("🔥 SCORE RESPONSE:", response.json())
                        st.session_state.lead_scores[lead_id] = response.json()
                        if lead_id not in st.session_state.activities:
                            st.session_state.activities[lead_id] = []

                        activity = {
                            "icon": "🎯",
                            "title": "AI Lead Score Generated"
                        }

                        if activity not in st.session_state.activities[lead_id]:
                            st.session_state.activities[lead_id].append(activity)
                        st.rerun()

                    else:

                        st.error("Unable to generate AI Lead Score.")
            else:

                lead_score = p.get("score")

                if lead_score is None:
                    st.warning("Lead score is not available.")
                    return
                col1, col2 = st.columns(2)

                with col1:
                    st.metric(
                        "🎯 Lead Score",
                        f"{lead_score}/100"
                    )
                    st.caption(f"AI Confidence Score: {lead_score}/100")
                    st.progress(lead_score / 100)

                with col2:
                    if lead_score >= 75:
                        priority = "High"
                    elif lead_score >= 50:
                        priority = "Medium"
                    else:
                        priority = "Low"

                    if priority == "High":
                        st.success(f"🟢 Priority: {priority}")

                    elif priority == "Medium":
                        st.warning(f"🟡 Priority: {priority}")

                    else:
                        st.error(f"🔴 Priority: {priority}")
                st.divider()

                st.subheader("🚀 Next Best Action")

                st.info(
                    "Prioritize this lead based on its current AI score and "
                    "continue with the appropriate sales engagement."
                )

                st.subheader("📝 AI Reasoning")

                st.write(
                    f"This lead currently has an AI score of {lead_score}/100. "
                    "The score is calculated using company profile, decision-maker, "
                    "technology fit, industry fit, budget, engagement, and conversation signals."
                )

                st.divider()

                # ============================================================
                # RECOMMENDATION ENGINE
                # ============================================================

                st.subheader("🎯 Recommendation Engine")

                if "lead_recommendations" not in st.session_state:
                    st.session_state.lead_recommendations = {}

                if lead_id not in st.session_state.lead_recommendations:

                    st.info(
                        "Generate an actionable engagement recommendation "
                        "based on the lead's score and engagement signals."
                    )

                    if st.button(
                        "💡 Generate Recommendation",
                        key=f"recommend_{lead_id}",
                        type="primary",
                        width="stretch"
                    ):

                        with st.spinner("🤖 Generating engagement recommendation..."):

                            recommendation_response = requests.post(
                                "http://127.0.0.1:8000/recommendation/predict",
                                json={
                                    "industry": p["industry"],
                                    "company": p.get("company", "Unknown"),
                                    "company_size": p.get("company_size", "Unknown"),
                                    "lead_status": p["status"],
                                    "lead_score": lead_score,
                                    "conversion_probability": 0,
                                    "engagement_score": p.get("engagement_score", 50),
                                    "tech_stack_match": p.get("tech_stack_match", 0),
                                    "budget_score": p.get("budget_score", 50)
                                }
                            )
                            if recommendation_response.status_code == 200:

                                recommendation = recommendation_response.json()

                                st.subheader("💡 Recommendation Engine")

                                col1, col2 = st.columns(2)

                                with col1:
                                    st.markdown("### ⏰ Follow-up Timing")
                                    st.info(recommendation["follow_up_timing"])

                                with col2:
                                    st.markdown("### 📡 Channel Mix")
                                    st.success(
                                        f"Primary: {recommendation['primary_channel']}\n\n"
                                        f"Secondary: {recommendation['secondary_channel']}"
                                    )

                                st.markdown("### 📝 Content Strategy")
                                st.write(recommendation["content_strategy"])

                                st.markdown("### 💡 Why this recommendation?")
                                st.caption(recommendation["reason"])

                            else:
                                st.error(
                                    f"Recommendation failed: "
                                    f"{recommendation_response.text}"
                                )

                        
                else:

                    recommendation = st.session_state.lead_recommendations[lead_id]

                    st.markdown("### ⏱️ Follow-up Timing")

                    st.info(
                        recommendation["follow_up_timing"]
                    )

                    st.markdown("### 📡 Channel Mix")

                    col1, col2 = st.columns(2)

                    with col1:
                        st.success(
                            f"**Primary Channel**\n\n"
                            f"{recommendation['primary_channel']}"
                        )

                    with col2:
                        st.info(
                            f"**Secondary Channel**\n\n"
                            f"{recommendation['secondary_channel']}"
                        )

                    st.markdown("### 📝 Content Strategy")

                    st.write(
                        recommendation["content_strategy"]
                    )

                    st.markdown("### 💡 Recommendation Reason")

                    st.caption(
                        recommendation["reason"]
                    )


        with conversation:
            st.subheader("💬 Conversation Intelligence")

            transcript = st.text_area(
                "Paste Meeting / Call Transcript",
                height=250,
                placeholder="Paste Zoom, Teams, Email or Sales Call transcript...",
                key=f"conversation_input_{p['id']}"
            )
            if st.button(
                "🚀 Analyze Conversation",
                key=f"conversation_{p['id']}",
                use_container_width=True
            ):
                st.write("Button clicked!")
                response = requests.post(
                    "http://127.0.0.1:8000/conversation/analyze",
                    json={
                        "lead_id": p["id"],
                        "transcript": transcript
                    }
                )
                print("🔥 OUTREACH STATUS:", response.status_code)
                print("🔥 OUTREACH RESPONSE:", response.text)
                if response.status_code == 200:

                    st.session_state[f"conversation_analysis_{p['id']}"] = {
                        "transcript": transcript,
                        "analysis": response.json()
                    }

                    if p["id"] not in st.session_state.activities:
                        st.session_state.activities[p["id"]] = []

                    activity_log = {
                        "icon": "💬",
                        "title": "Conversation analyzed with AI"
                    }

                    if activity_log not in st.session_state.activities[p["id"]]:
                        st.session_state.activities[p["id"]].append(activity_log)

                    st.rerun()

                else:
                    st.error("Unable to analyze conversation.")
            if f"conversation_analysis_{p['id']}" in st.session_state:

                data = st.session_state[f"conversation_analysis_{p['id']}"]["analysis"]

                st.divider()

                st.subheader("📄 Meeting Summary")
                
                col1, col2 = st.columns(2)

                with col1:
                    st.metric("😊 Sentiment", data["sentiment"])

                with col2:
                    st.metric("🔥 Buying Intent", data["buying_intent"])

                st.subheader("⚠️ Pain Points")

                for point in data["pain_points"]:
                    st.write(f"• {point}")

                st.subheader("❌ Objections")

                for obj in data["objections"]:
                    st.write(f"• {obj}")

                st.subheader("➡️ Next Actions")

                for action in data["next_actions"]:
                    st.success(action)

                st.subheader("📝 CRM Notes")
                st.write(data["crm_notes"])
                if st.button(
                    "💾 Save to CRM",
                    key=f"save_conversation_{p['id']}",
                    use_container_width=True
                ):

                    requests.post(
                        "http://127.0.0.1:8000/conversation/save",
                        json={
                            "lead_id": p["id"],
                            "transcript": st.session_state[f"conversation_analysis_{p['id']}"]["transcript"],
                            "summary": data["summary"],
                            "sentiment": data["sentiment"],
                            "buying_intent": data["buying_intent"],
                            "next_action": "\n".join(data["next_actions"]),
                            "crm_notes": data["crm_notes"]
                        }
                    )

                    st.success("✅ Conversation saved successfully!")

                    activity_log = {
                        "icon": "💾",
                        "title": "Conversation saved to CRM"
                    }

                    if activity_log not in st.session_state.activities[p["id"]]:
                        st.session_state.activities[p["id"]].append(activity_log)
        with activity:

            st.markdown("### 📅 Activity Timeline")

            activities = st.session_state.activities.get(p["id"], [])

            if not activities:
                st.info("No activities yet.")

            for activity in activities:
                st.write(f"{activity['icon']}  {activity['title']}")
            st.markdown("---")

            st.write("Upcoming Task")

            st.checkbox(
                "Schedule Follow-up Call"
            )

        # ======================================================

        with notes:

            st.text_area(

                "Internal Notes",

                value=p["notes"],

                height=220

            )

            return
        st.title("👥 Leads & Prospects")

        st.caption(
            "Manage prospects, monitor AI lead scores and track outreach."
        )

        dashboard_cards()

        st.divider()

        show_charts()

        st.divider()
        # ==========================================================
    # SEARCH + ACTION BAR
    # ==========================================================

    left, middle, right = st.columns([5,2,2])

    with left:

        search = st.text_input(
            "Search",
            placeholder="🔍 Search company...",
            label_visibility="collapsed"
        )

    with middle:

        uploaded_file = st.file_uploader(
        "Import CSV",
        type=["csv"],
        label_visibility="collapsed"
    )

    with right:

        if st.button(
            "➕ Add Prospect",
            type="primary",
            use_container_width=True
        ):
            st.session_state.show_form = True

    if uploaded_file is not None:

        if st.button(
            "📥 Import CSV",
            use_container_width=True
        ):

            files = {
                "file": (
                    uploaded_file.name,
                    uploaded_file.getvalue(),
                    "text/csv"
                )
            }

            response = requests.post(
                "http://127.0.0.1:8000/leads/import",
                files=files
            )

            if response.status_code == 200:

                st.success(
                    response.json()["message"]
                )

                st.rerun()

            else:

                st.error(
                    f"CSV Import Failed: "
                    f"{response.status_code}"
                )

                st.code(response.text)

    st.divider()

    st.subheader("Prospects")

    # ==========================================================
    # FILTER
    # ==========================================================

    filtered = []

    for p in prospects:

        if search.lower() in p["company"].lower():
            filtered.append(p)
        

    # ==========================================================
    # AI Recommendation Panel
    # ==========================================================

    highest = None

    for p in filtered:

        if p["id"] in st.session_state.lead_scores:

            current_score = st.session_state.lead_scores[p["id"]]["lead_score"]

            if highest is None or current_score > highest["_ai_score"]:
                highest = {
                    **p,
                    "_ai_score": current_score
                }
    if highest:
        st.markdown(
            f"""
            ### 🤖 AI Recommendation
            **{highest['company']}**

            Highest AI Lead Score: **{highest['_ai_score']}/100**

            Recommendation:
            ✔ Prioritize outreach this week.
            """
        )

        st.progress(highest["_ai_score"] / 100)

        st.caption(
            f"AI Lead Score: {highest['_ai_score']}/100"
        )

    st.divider()
    if st.button(
    "🔄 Re-analyze All",
    use_container_width=True
    ):

        response = requests.post(
            "http://127.0.0.1:8000/leads/reanalyze"
        )

        if response.status_code == 200:
            st.write(response.status_code)
            st.write(response.json())
            st.rerun()
        else:
            st.error("Failed to re-analyze leads.")
    # ==========================================================
    # PROSPECT CARDS
    # ==========================================================

    for p in filtered:

        with st.container(border=True):

            left,right = st.columns([5,2])

            with left:

                st.markdown(
                    f"## 🏢 {p['company']}"
                )

                st.caption(
                    f"{p['industry']} • {p['location']}"
                )

                c1,c2 = st.columns(2)

                with c1:

                    st.write(
                        f"👤 **{p['contact']}**"
                    )

                    st.caption(
                        p["designation"]
                    )

                with c2:

                    status_badge(
                        p["status"]
                    )

            with right:

                # Use the latest AI-generated score if available
                ai_score = p.get("score")
                if ai_score is not None:

                    st.metric(
                        "🎯 AI Lead Score",
                        f"{ai_score}/100"
                    )

                    st.progress(
                        ai_score / 100
                    )

                else:

                    st.metric(
                        "🎯 AI Lead Score",
                        "Not calculated"
                    )
                st.write("")

                if st.button(
                    "👁 View Details",
                    key=f"view_{p['id']}",
                    use_container_width=True
                ):

                    lead = requests.get(
                        f"http://127.0.0.1:8000/leads/{p['id']}"
                    ).json()

                    st.session_state.selected_prospect = lead

                    st.rerun()
                edit_left, edit_button, edit_right = st.columns([1, 2, 1])

                with edit_button:
                        if st.button(
                            "✏️ Edit",
                            key=f"edit_{p['id']}",
                            use_container_width=True
                        ):
                            edit_prospect_dialog(p)
                
                st.markdown("---")
    # ==========================================================
    # ADD PROSPECT FORM
    # ==========================================================
    
    if st.session_state.get("show_form", False):

        st.divider()

        st.markdown("## ➕ Create New Prospect")

        with st.container(border=True):

            with st.form("prospect_form", clear_on_submit=True):

                # ============================================================
                # PROSPECT INFORMATION
                # ============================================================

                col1, col2 = st.columns(2)

                with col1:

                    company = st.text_input(
                        "🏢 Company Name *"
                    )

                    industry = st.selectbox(
                        "🏭 Industry",
                        [
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
                    )

                    location = st.text_input(
                        "📍 Location"
                    )

                    website = st.text_input(
                        "🌐 Website"
                    )

                with col2:

                    contact = st.text_input(
                        "👤 Contact Person *"
                    )

                    designation = st.text_input(
                        "💼 Designation"
                    )

                    email = st.text_input(
                        "📧 Email"
                    )

                    phone = st.text_input(
                        "📞 Phone"
                    )

                # ============================================================
                # SALES / PIPELINE INFORMATION
                # ============================================================

                st.markdown("### 💼 Sales & Pipeline Information")

                pipeline_col1, pipeline_col2 = st.columns(2)

                with pipeline_col1:

                    deal_value = st.number_input(
                        "💰 Pipeline Value",
                        min_value=0.0,
                        value=0.0,
                        step=1000.0,
                        help="Estimated value of the potential deal."
                    )

                with pipeline_col2:

                    pipeline_status = st.selectbox(
                        "📊 Pipeline Status",
                        [
                            "New",
                            "Qualified",
                            "Contacted",
                            "Proposal",
                            "Negotiation",
                            "Won",
                            "Lost"
                        ]
                    )

                # ============================================================
                # NOTES
                # ============================================================

                notes = st.text_area(
                    "📝 Notes",
                    placeholder="Add important notes about this prospect..."
                )

                # ============================================================
                # ACTION BUTTONS
                # ============================================================

                save_col, cancel_col = st.columns(2)

                with save_col:

                    save = st.form_submit_button(
                        "💾 Save Prospect",
                        use_container_width=True
                    )

                with cancel_col:

                    cancel = st.form_submit_button(
                        "❌ Cancel",
                        use_container_width=True
                    )

                # ============================================================
                # SAVE PROSPECT
                # ============================================================

                if save:

                    if company.strip() == "" or contact.strip() == "":

                        st.error(
                            "Company Name and Contact Person are required."
                        )

                    else:

                        response = requests.post(
                            "http://127.0.0.1:8000/leads/",
                            json={
                                "company": company,
                                "contact": contact,
                                "designation": designation,
                                "email": email,
                                "phone": phone,
                                "website": website,
                                "location": location,
                                "industry": industry,
                                "notes": notes,

                                # Sales / Pipeline fields
                                "deal_value": deal_value,
                                "status": pipeline_status
                            }
                        )

                        print("🔥 CREATE PROSPECT RESPONSE:")
                        print(response.status_code)
                        print(response.text)

                        if response.status_code in [200, 201]:

                            st.success(
                                "✅ Prospect created successfully!"
                            )

                            st.balloons()

                            # Close form
                            st.session_state.show_form = False

                            # Clear cached prospect data
                            st.session_state.pop(
                                "prospects",
                                None
                            )

                            # Refresh page
                            st.rerun()

                        else:

                            st.error(
                                f"Unable to create prospect.\n\n"
                                f"{response.text}"
                            )

                # ============================================================
                # CANCEL
                # ============================================================

                if cancel:

                    st.session_state.show_form = False

                    st.rerun()
