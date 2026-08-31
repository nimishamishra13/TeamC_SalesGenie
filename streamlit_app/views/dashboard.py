import streamlit as st
import requests
import plotly.express as px
import pandas as pd

from components.header import show_header
from components.stat_cards import show_stat_cards
from components.welcome import show_welcome
from components.recent_activity import show_recent_activity

BASE_URL = "http://127.0.0.1:8000"

def get_leads():
    try:
        response = requests.get("http://127.0.0.1:8000/leads/")
        response.raise_for_status()
        return response.json()
    except Exception:
        return []


def show_dashboard():

    leads = get_leads()
    df = pd.DataFrame(leads)
    total_leads = len(leads)
    hot_leads = len([lead for lead in leads if lead.get("status") == "Hot"])
    warm_leads = len([lead for lead in leads if lead.get("status") == "Warm"])
    avg_score = (
        round(sum(lead.get("score", 0) for lead in leads) / total_leads)
        if total_leads > 0
        else 0
    )

    show_header()

    show_stat_cards(
        total_leads=total_leads,
        hot_leads=hot_leads,
        warm_leads=warm_leads,
        avg_score=avg_score,
    )

    left, right = st.columns([2, 1])

    with left:
        show_welcome()

    if not df.empty:

        st.markdown("### 📊 Sales Analytics")

        chart1, chart2 = st.columns(2)

        # Pie Chart - Lead Status
        with chart1:
            status_counts = df["status"].value_counts().reset_index()
            status_counts.columns = ["Status", "Count"]

            fig = px.pie(
                status_counts,
                values="Count",
                names="Status",
                title="Lead Status Distribution",
                hole=0.45,
            )

            st.plotly_chart(fig, use_container_width=True)

        # Bar Chart - Lead Scores
        with chart2:
            fig = px.histogram(
                df,
                x="score",
                nbins=10,
                title="Lead Score Distribution",
            )
            fig.update_yaxes(
                tickmode="linear",
                dtick=1,
                tickformat="d"
            )

            st.plotly_chart(fig, use_container_width=True)

def get_api(endpoint):

    try:

        response = requests.get(
            f"{BASE_URL}{endpoint}",
            timeout=10
        )

        if response.status_code == 200:
            return response.json()

        st.error(
            f"API error {response.status_code}: "
            f"{response.text}"
        )

    except Exception as e:

        st.error(
            f"Unable to connect to backend: {e}"
        )

    return None
def show_dashboard():

    st.title("📊 Sales Analytics")

    st.caption(
        "Sales performance, pipeline intelligence "
        "and AI-powered follow-up recommendations"
    )

    # =====================================================
    # KPI DATA
    # =====================================================

    summary = get_api(
        "/dashboard/summary"
    )

    pipeline_data = get_api(
        "/dashboard/pipeline"
    )

    pipeline_value_data = get_api(
        "/dashboard/pipeline-value"
    )

    sales_cycle_data = get_api(
        "/dashboard/sales-cycle"
    )

    score_data = get_api(
        "/dashboard/scores"
    )

    if summary is None:
        return

        # =====================================================
        # KPI CARDS
        # =====================================================

    total_leads = summary.get(
            "total_leads", 0
        )

    conversion_rate = summary.get(
            "conversion_rate", 0
        )
    pipeline_value = (
            pipeline_value_data or {}
        ).get(
            "pipeline_value", 0
        )

    average_cycle = (
            sales_cycle_data or {}
        ).get(
            "average_sales_cycle_days", 0
        )

    average_score = (
            score_data or {}
        ).get(
            "average_score", 0
        )
    col1, col2, col3, col4 = st.columns(4)

    with col1:

            st.metric(
                "👥 Total Leads",
                total_leads
            )

    with col2:

            st.metric(
                "📈 Conversion Rate",
                f"{conversion_rate}%"
            )

    with col3:

            st.metric(
                "💰 Pipeline Value",
                f"₹{pipeline_value:,.0f}"
            )

    with col4:

            st.metric(
                "⏱ Avg Sales Cycle",
                f"{average_cycle} days"
            )
    st.divider()

        # =====================================================
        # SECONDARY KPIs
        # =====================================================

    col1, col2, col3 = st.columns(3)

    with col1:

            st.metric(
                "🤖 Average AI Score",
                f"{average_score:.1f}"
            )

    with col2:

            st.metric(
                "🔥 High Quality Leads",
                (
                    score_data or {}
                ).get(
                    "high_quality_leads", 0
                )
            )

    with col3:

            st.metric(
                "🏆 Won Leads",
                summary.get(
                    "won_leads", 0
                )
            )
    st.divider()

    # =====================================================
    # PIPELINE OVERVIEW
    # =====================================================

    st.subheader(
        "📊 Pipeline Overview"
    )

    pipeline = (
        pipeline_data or {}
    ).get(
        "pipeline", {}
    )

    if pipeline:

        st.bar_chart(
            pipeline
        )

    else:

        st.info(
            "No pipeline data available."
        )

    st.divider()
    # =====================================================
    # KANBAN PIPELINE
    # =====================================================

    st.subheader(
        "📋 Sales Pipeline"
    )

    show_kanban()

    st.divider()

    # =====================================================
    # FOLLOW-UP RECOMMENDATIONS
    # =====================================================

    show_recommendations()


# =========================================================
# KANBAN
# =========================================================
def show_kanban():

    leads = get_api(
        "/leads/"
    )

    if not leads:

        st.info(
            "No leads available."
        )

        return

    stages = [
        "New",
        "Contacted",
        "Qualified",
        "Proposal Sent",
        "Negotiation",
        "Won",
        "Lost"
    ]

    columns = st.columns(
        len(stages)
    )

    for column, stage in zip(
        columns,
        stages
    ):

        with column:

            st.markdown(
                 f"### {stage}"
            )

            stage_leads = [

                lead

                for lead in leads

                if (
                    lead.get("status") or ""
                ).lower().strip()
                ==
                stage.lower()
            ]

            if not stage_leads:

                st.caption(
                    "No leads"
                )

            for lead in stage_leads:

                score = lead.get(
                    "score"
                )

                company = lead.get(
                    "company",
                    "Unknown"
                )

                contact = lead.get(
                    "contact",
                    "Unknown"
                )
                deal_value = lead.get(
                    "deal_value",
                    0
                ) or 0

                with st.container(
                    border=True
                ):

                    st.markdown(
                        f"**🏢 {company}**"
                    )

                    st.caption(
                        f"👤 {contact}"
                    )

                    if score is not None:

                        st.write(
                            f"🎯 Score: **{score}/100**"
                        )

                    else:

                        st.write(
                            "🎯 Score: Not calculated"
                        )

                    st.write(
                        f"💰 ₹{deal_value:,.0f}"
                    )

                    if score is not None:
                         st.progress(
                            min(
                                score / 100,
                                1.0
                            )
                        )


# =========================================================
# AI RECOMMENDATIONS
# =========================================================

def show_recommendations():

    st.subheader(
        "🤖 AI Follow-up Recommendations"
    )

    data = get_api(
        "/dashboard/recommendations"
    )

    if not data:

        st.info(
            "No recommendations available."
        )

        return
    recommendations = data.get(
        "recommendations",
        []
    )

    if not recommendations:

        st.info(
            "No follow-up recommendations."
        )

        return

    # Show highest-scoring leads first

    recommendations = sorted(
        recommendations,
        key=lambda x: x.get(
            "score", 0
        ),
        reverse=True
    )

    for recommendation in recommendations[:5]:

        priority = recommendation.get(
            "priority",
            "Low"
        )

        company = recommendation.get(
            "company",
            "Unknown"
        )

        score = recommendation.get(
             "score",
            0
        )

        action = recommendation.get(
            "recommended_action",
            "Review lead"
        )

        if priority == "High":

            icon = "🔥"

        elif priority == "Medium":

            icon = "🟡"

        else:

            icon = "🟢"

        with st.container(
            border=True
        ):

            st.markdown(
                f"### {icon} {company}"
            )

            col1, col2 = st.columns(2)

            with col1:

                st.write(
                    f"🎯 AI Score: **{score}/100**"
                )
            with col2:

                st.write(
                    f"Priority: **{priority}**"
                )

            st.info(
                f"**Next Action:** {action}"
            )
