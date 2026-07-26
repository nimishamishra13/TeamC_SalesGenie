import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os

sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..")
    )
)
from ai.ai_analysis import analyze_lead
from views.ai_panel import show_ai_analysis
# ==========================================================
# SAMPLE DATA
# ==========================================================

import requests

try:
    response = requests.get("http://127.0.0.1:8000/leads")
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

def dashboard_cards(prospects):

    total = len(prospects)

    hot = len([p for p in prospects if p["status"]=="Hot"])

    warm = len([p for p in prospects if p["status"]=="Warm"])

    avg = int(
        sum(p["score"] for p in prospects)/len(prospects)
    )

    c1,c2,c3,c4 = st.columns(4)

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
            "⭐ Avg Score",
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

    company = st.text_input("🏢 Company", value=p["company"])
    industry = st.text_input("🏭 Industry", value=p["industry"])
    location = st.text_input("📍 Location", value=p["location"])
    website = st.text_input("🌐 Website", value=p["website"])

    contact = st.text_input("👤 Contact", value=p["contact"])
    designation = st.text_input("💼 Designation", value=p["designation"])
    email = st.text_input("📧 Email", value=p["email"])
    phone = st.text_input("📞 Phone", value=p["phone"])

    notes = st.text_area(
        "📝 Notes",
        value=p["notes"],
        height=120
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("💾 Save Changes", use_container_width=True):

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
                    "notes": notes
                }
            )

            if response.status_code == 200:
                st.success("Lead updated successfully!")
                st.rerun()
            else:
                st.error("Update failed.")

    with col2:
        if st.button("Cancel", use_container_width=True):
            st.rerun()

# ==========================================================
# MAIN PAGE
# ==========================================================

def show_leads():
    try:
        response = requests.get("http://127.0.0.1:8000/leads")
        response.raise_for_status()
        prospects = response.json()
    except Exception as e:
        st.error(f"Backend not running: {e}")
        prospects = [] 

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

            st.metric(
                "⭐ Lead Score",
                f"{p['score']}/100"
            )

            st.progress(
                p["score"]/100
            )

        with c2:

            st.metric(
                "Status",
                p["status"]
            )

            status_badge(
                p["status"]
            )

        with c3:

            st.metric(
                "Priority",
                "High" if p["score"] >= 90 else "Medium"
            )

        st.divider()

        overview, ai, activity, notes = st.tabs(

            [

                "🏢 Overview",

                "🤖 AI Insights",

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

        with activity:

            st.markdown("### 📅 Activity Timeline")

            st.success("✅ Prospect Created")

            st.info("📧 Outreach Email Sent")

            st.warning("⏳ Awaiting Response")

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
            "➕ Add Lead",
            type="primary",
            use_container_width=True
        ):
            st.session_state.show_form = True

    if uploaded_file is not None:
    
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
                st.success(response.json()["message"])
                st.rerun()
            else:
                st.error("CSV Import Failed")
        


    

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

    highest = max(filtered, key=lambda x: x["score"]) if filtered else None

    if highest:
        st.markdown(
            f"""
            ### 🤖 AI Recommendation
            **{highest['company']}**
            Highest Lead Score
            Recommendation:
            ✔ Prioritize outreach this week.
            """
        )

        st.progress(highest["score"]/100)

        st.caption(
            f"Confidence: {highest['score']}%"
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

                st.metric(
                    "Lead Score",
                    f"{p['score']}/100"
                )

                st.progress(
                    p["score"]/100
                )

                st.write("")

                if st.button(
                    "👁 View Details",
                    key=f"view_{p['company']}",
                    use_container_width=True
                ):

                    lead = requests.get(
                        f"http://127.0.0.1:8000/leads/{p['id']}"
                    ).json()

                    st.session_state.selected_prospect = lead

                    st.rerun()
                if st.button("✏️ Edit", key=f"edit_{p['id']}"):
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

                notes = st.text_area(
                    "📝 Notes",
                    placeholder="Add important notes about this prospect..."
                )

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

                if save:

                    if company == "" or contact == "":

                        st.error(
                            "Company Name and Contact Person are required."
                        )

                    else:

                        requests.post(
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
                                "notes": notes
                            }
                        )
                        st.success(
                            "✅ Prospect created successfully!"
                        )

                        st.balloons()

                        st.session_state.show_form = False

                        st.rerun()

                if cancel:

                    st.session_state.show_form = False

                    st.rerun()
    