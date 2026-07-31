import streamlit as st
import requests

LOGIN_URL = "http://127.0.0.1:8000/auth/login"


def show_login():
    st.title("SalesGenie")
    st.subheader("Login")

    email = st.text_input("Email", key="login_email")
    password = st.text_input(
        "Password",
        type="password",
        key="login_password"
    )

    if st.button("Login", use_container_width=True, key="login_button"):

        if not email or not password:
            st.warning("Please enter email and password.")
        else:
            try:
                response = requests.post(
                    LOGIN_URL,
                    json={
                        "email": email,
                        "password": password
                    },
                    timeout=5
                )

                if response.status_code == 200:
                    data = response.json()

                    st.session_state["logged_in"] = True
                    st.session_state["user"] = data["user"]

                    st.rerun()

                elif response.status_code == 401:
                    st.error("Invalid email or password.")

                else:
                    st.error(
                        f"Login failed. Status code: {response.status_code}"
                    )

            except requests.RequestException as e:
                st.error(f"Unable to connect to backend: {e}")

    st.divider()

    if st.button(
        "Don't have an account? Sign Up",
        key="go_to_register"
    ):
        st.session_state["auth_page"] = "register"
        st.rerun()