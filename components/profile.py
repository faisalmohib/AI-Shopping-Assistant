import streamlit as st


def show_profile():

    user = st.session_state.user

    st.subheader("👤 My Profile")

    st.write(f"**Name:** {user['full_name']}")

    st.write(f"**Email:** {user['email']}")

