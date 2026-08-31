import streamlit as st

def show_header():
    col1, col2 = st.columns([4, 1])

    with col1:
        st.title("Overview")
        st.caption("Manage your prospects and sales pipeline")
