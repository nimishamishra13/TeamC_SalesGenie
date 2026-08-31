import streamlit as st
from ai.ai_analysis import analyze_lead, build_lead_analysis
from ai.tech_stack import detect_tech_stack

def show_ai_analysis(lead):

    if "ai_reports" not in st.session_state:
        st.session_state.ai_reports = {}

    lead_id = lead["id"]

    if st.button(
        "🚀 Analyze Lead with AI",
        key=f"ai_{lead_id}"
    ):
        report = build_lead_analysis(lead)

        st.session_state.ai_reports[lead_id] = report

        # Initialize activities if needed
        if "activities" not in st.session_state:
            st.session_state.activities = {}

        if lead_id not in st.session_state.activities:
            st.session_state.activities[lead_id] = []

        activity = {
            "icon": "🤖",
            "title": "AI Analysis Completed"
        }

        if activity not in st.session_state.activities[lead_id]:
            st.session_state.activities[lead_id].append(activity)


    if lead_id in st.session_state.ai_reports:

        report = st.session_state.ai_reports[lead_id]

        st.subheader("🛠 Tech Stack Ingestion")

        if report["tech_stack"]:
            for tech in report["tech_stack"]:
                st.success(tech)
        else:
            st.info("No technologies detected")
        st.subheader("Executive Summary")
        st.write(report["executive_summary"])

        st.subheader("Strengths")
        for item in report["strengths"]:
            st.success(item)

        st.subheader("Risks")
        for item in report["risks"]:
            st.warning(item)

        st.subheader("Sales Strategy")
        st.info(report["sales_strategy"])

        st.subheader("Next Best Action")
        st.success(report["next_action"])
