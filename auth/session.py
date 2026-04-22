import streamlit as st


def init_session():
    if "logged_in" not in st.session_state:
        st.session_state.update({
            "logged_in": False,
            "email": "",
            "first_name": "",
            "last_name": "",
            "id_token": "",
        })
