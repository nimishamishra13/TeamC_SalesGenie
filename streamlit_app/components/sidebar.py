import streamlit as st


def show_sidebar():

    with st.sidebar:

        st.markdown("# **SalesGenie**")
        st.caption("AI Sales Assistant")

        # Show logged-in user
        user = st.session_state.get("user")

        if user:
            st.write(f"👤 {user.get('name', 'User')}")
            st.caption(user.get("email", ""))

        st.divider()

        page = st.radio(
            "Navigation",
            [
                "📊 Overview",
                "👥 Leads",
                "⚙️ Settings",
                "🚪 Logout"
            ],
            label_visibility="collapsed"
        )

        if page == "🚪 Logout":

            st.session_state.clear()

            st.rerun()

    return page