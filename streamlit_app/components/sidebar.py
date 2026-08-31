import streamlit as st


def show_sidebar():

    with st.sidebar:

        # ==============================
        # BRAND
        # ==============================

        st.markdown("## ✦ SalesGenie")
        st.caption("AI Sales Assistant")

        st.divider()

        # ==============================
        # MENU
        # ==============================

        st.caption("MAIN MENU")

        page = st.radio(
            "Navigation",
            [
                "📊  Overview",
                "👥  Leads",
                "⚙️  Settings",
                "🚪  Logout"
            ],
            label_visibility="collapsed"
        )

        # ==============================
        # USER
        # ==============================

        user = st.session_state.get("user")

        if user:

            name = user.get("name", "User")
            email = user.get("email", "")

            st.divider()

            st.caption("WORKSPACE")

            st.markdown(f"**👤 {name}**")
            st.caption(email)

            st.markdown("🟢 **Active**")

        # ==============================
        # LOGOUT
        # ==============================

        if page == "🚪  Logout":

            st.session_state.clear()
            st.rerun()

    return page
