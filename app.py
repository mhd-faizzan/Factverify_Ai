import streamlit as st
from config.settings import configure_page
from config.styles import inject_styles
from auth.session import init_session, is_token_expired
from ui.auth_page import show_auth_ui
from ui.main_page import show_main_app

configure_page()
inject_styles()
init_session()

# auto-logout if Firebase token has expired (after ~55 min)
if st.session_state.logged_in and is_token_expired():
    st.session_state.clear()
    st.warning("Your session expired. Please log in again.")
    st.rerun()

if not st.session_state.logged_in:
    show_auth_ui()
else:
    show_main_app()

