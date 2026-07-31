import streamlit as st
from pathlib import Path
from views.settings import show_settings
from components.sidebar import show_sidebar
from views.dashboard import show_dashboard
from views.leads import show_leads
from views.login import show_login
from views.register import show_register


st.set_page_config(
    page_title="SalesGenie",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


style_path = Path(__file__).parent / "style.css"

if style_path.exists():
    with open(style_path) as f:
        st.markdown(
            f"<style>{f.read()}</style>",
            unsafe_allow_html=True
        )


if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if "auth_page" not in st.session_state:
    st.session_state["auth_page"] = "login"


if not st.session_state["logged_in"]:

    if st.session_state["auth_page"] == "register":
        show_register()
    else:
        show_login()

    st.stop()


page = show_sidebar()


if page == "📊 Overview":
    show_dashboard()

elif page == "👥 Leads":
    show_leads()

elif page == "⚙️ Settings":
    show_settings()