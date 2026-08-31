import streamlit as st
from views.settings import show_settings
from components.sidebar import show_sidebar
from views.dashboard import show_dashboard
from views.leads import show_leads
from views.login import show_login
from views.register import show_register
from views.forgot_password import show_forgot_password

st.set_page_config(
    page_title="SalesGenie",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if "auth_page" not in st.session_state:
    st.session_state["auth_page"] = "login"


if not st.session_state["logged_in"]:

    if st.session_state["auth_page"] == "login":
        show_login()

    elif st.session_state["auth_page"] == "register":
        show_register()

    elif st.session_state["auth_page"] == "forgot_password":
        show_forgot_password()

    st.stop()

page = show_sidebar()
if "current_page" not in st.session_state:
    st.session_state.current_page = "leads"

if page == "📊  Overview":
    st.session_state.current_page = "overview"

if page == "👥  Leads" and st.session_state.current_page != "outreach":
    st.session_state.current_page = "leads"

if st.session_state.current_page == "overview":
    show_dashboard()

elif st.session_state.current_page == "leads":
    show_leads()

elif st.session_state.current_page == "settings":
    show_settings()
