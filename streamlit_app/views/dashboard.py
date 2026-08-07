import streamlit as st
import requests
import plotly.express as px
import pandas as pd

from components.header import show_header
from components.stat_cards import show_stat_cards
from components.welcome import show_welcome
from components.recent_activity import show_recent_activity


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

        st.markdown("---")

        # Company-wise Leads
        company_counts = (
            df["company"]
            .value_counts()
            .head(10)
            .reset_index()
        )

        company_counts.columns = ["Company", "Leads"]

        fig = px.bar(
            company_counts,
            x="Leads",
            y="Company",
            orientation="h",
            title="Top Companies"
        )
        fig.update_xaxes(
            tickmode="linear",
            dtick=1,
            tickformat="d"
        )

        st.plotly_chart(fig, use_container_width=True)
