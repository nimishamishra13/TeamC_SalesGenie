import streamlit as st
import requests

RESET_URL = "http://127.0.0.1:8000/auth/reset-password"


def show_forgot_password():

    st.title("Reset Password")

    email = st.text_input(
        "Email",
        key="reset_email"
    )

    new_password = st.text_input(
        "New Password",
        type="password",
        key="reset_password"
    )

    if st.button(
        "Reset Password",
        use_container_width=True
    ):

        try:

            response = requests.post(
                RESET_URL,
                json={
                    "email": email,
                    "new_password": new_password
                },
                timeout=5
            )

            if response.status_code == 200:

                st.success("Password reset successful.")

                st.session_state["auth_page"] = "login"

                st.rerun()

            else:

                st.error(response.json()["detail"])

        except requests.RequestException as e:

            st.error(f"Unable to connect to backend: {e}")

    st.divider()

    if st.button(
        "← Back to Login",
        use_container_width=True
    ):

        st.session_state["auth_page"] = "login"

        st.rerun()
