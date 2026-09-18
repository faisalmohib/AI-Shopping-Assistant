import streamlit as st

from services.auth_service import register_user


def show_register():

    st.subheader("📝 Register")

    with st.form("register_form"):

        full_name = st.text_input("Full Name")

        email = st.text_input("Email")

        password = st.text_input(
            "Password",
            type="password"
        )

        confirm_password = st.text_input(
            "Confirm Password",
            type="password"
        )

        submit = st.form_submit_button(
            "Create Account"
        )

        if submit:

            if not full_name or not email or not password:

                st.error("Please fill all fields.")

            elif password != confirm_password:

                st.error("Passwords do not match.")

            elif len(password) < 6:

                st.error(
                    "Password must be at least 6 characters."
                )

            else:

                success, message = register_user(
                    full_name,
                    email,
                    password
                )

                if success:
                    st.success(message)

                else:
                    st.error(message)