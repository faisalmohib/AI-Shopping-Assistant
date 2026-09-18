import streamlit as st

from services.auth_service import login_user


def show_login():

    st.subheader("🔐 Login")

    with st.form("login_form"):

        email = st.text_input("Email")

        password = st.text_input(
            "Password",
            type="password"
        )

        submit = st.form_submit_button(
            "Login"
        )

        if submit:

            user = login_user(
                email,
                password
            )

            if user:

                st.session_state.user = user

                st.success(
                    f"Welcome, {user['full_name']}!"
                )

                st.rerun()

            else:

                st.error(
                    "Invalid email or password."
                )