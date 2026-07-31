import streamlit as st
import requests

REGISTER_URL = "http://127.0.0.1:8000/auth/register"


def show_register():
    st.title("SalesGenie")
    st.subheader("Create Account")

    name = st.text_input(
        "Name",
        key="register_name"
    )

    email = st.text_input(
        "Email",
        key="register_email"
    )

    password = st.text_input(
        "Password",
        type="password",
        key="register_password"
    )

    confirm_password = st.text_input(
        "Confirm Password",
        type="password",
        key="register_confirm_password"
    )

    if st.button(
        "Create Account",
        use_container_width=True,
        key="register_button"
    ):

        if not name or not email or not password or not confirm_password:
            st.warning("Please fill in all fields.")

        elif password != confirm_password:
            st.error("Passwords do not match.")

        else:
            try:
                response = requests.post(
                    REGISTER_URL,
                    json={
                        "name": name,
                        "email": email,
                        "password": password
                    },
                    timeout=5
                )

                if response.status_code in (200, 201):
                    st.success("Account created successfully!")

                    st.session_state["auth_page"] = "login"

                    st.rerun()

                elif response.status_code == 400:
                    try:
                        st.error(response.json().get(
                            "detail",
                            "Registration failed."
                        ))
                    except ValueError:
                        st.error("Registration failed.")

                else:
                    st.error(
                        f"Registration failed. "
                        f"Status code: {response.status_code}"
                    )

            except requests.RequestException as e:
                st.error(f"Unable to connect to backend: {e}")

    st.divider()

    if st.button(
        "Already have an account? Login",
        key="go_to_login"
    ):
        st.session_state["auth_page"] = "login"
        st.rerun()