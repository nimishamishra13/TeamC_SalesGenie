import streamlit as st


def show_settings():
    st.title("⚙️ Settings")
    st.caption("Manage your SalesGenie account")

    st.divider()

    user = st.session_state.get("user", {})

    st.subheader("Profile")

    name = user.get("name", "User")
    email = user.get("email", "")

    st.text_input(
        "Name",
        value=name,
        disabled=True
    )

    st.text_input(
        "Email",
        value=email,
        disabled=True
    )

    st.info(
        "Profile editing and password change can be added later."
    )
