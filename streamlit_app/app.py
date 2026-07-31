import streamlit as st

from components.sidebar import show_sidebar
from views.dashboard import show_dashboard
from views.leads import show_leads
st.set_page_config(
    page_title="SalesGenie",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

page = show_sidebar()
if "current_page" not in st.session_state:
    st.session_state.current_page = "leads"
st.write(page)   # <-- temporary debugging

if page == "📊 Overview":
    st.session_state.current_page = "overview"

if page == "👥 Leads" and st.session_state.current_page != "outreach":
    st.session_state.current_page = "leads"

if st.session_state.current_page == "overview":
    show_dashboard()

elif st.session_state.current_page == "leads":
    show_leads()

elif st.session_state.current_page == "outreach":
    show_outreach()
