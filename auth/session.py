import streamlit as st
from datetime import datetime, timedelta

MAX_ATTEMPTS = 5
LOCKOUT_MINUTES = 15
TOKEN_LIFETIME_MINUTES = 55  # Firebase tokens last 60 min, we refresh 5 min early


def init_session():
    if "logged_in" not in st.session_state:
        st.session_state.update({
            "logged_in": False,
            "email": "",
            "first_name": "",
            "last_name": "",
            "id_token": "",
            "token_expiry": None,
            "login_attempts": 0,
            "lockout_until": None,
        })


def is_locked_out() -> bool:
    lockout = st.session_state.get("lockout_until")
    if lockout and datetime.now() < lockout:
        return True
    # clear lockout if time has passed
    if lockout:
        st.session_state.lockout_until = None
        st.session_state.login_attempts = 0
    return False


def record_failed_attempt():
    st.session_state.login_attempts = st.session_state.get("login_attempts", 0) + 1
    if st.session_state.login_attempts >= MAX_ATTEMPTS:
        st.session_state.lockout_until = datetime.now() + timedelta(minutes=LOCKOUT_MINUTES)


def reset_attempts():
    st.session_state.login_attempts = 0
    st.session_state.lockout_until = None


def set_token(id_token: str):
    st.session_state.id_token = id_token
    st.session_state.token_expiry = datetime.now() + timedelta(minutes=TOKEN_LIFETIME_MINUTES)


def is_token_expired() -> bool:
    expiry = st.session_state.get("token_expiry")
    if not expiry:
        return True
    return datetime.now() > expiry


def validate_password(password: str) -> str | None:
    # returns an error string, or None if valid
    if len(password) < 8:
        return "Password must be at least 8 characters."
    if not any(c.isupper() for c in password):
        return "Password must contain at least one uppercase letter."
    if not any(c.isdigit() for c in password):
        return "Password must contain at least one number."
    return None


def lockout_remaining() -> int:
    lockout = st.session_state.get("lockout_until")
    if not lockout:
        return 0
    remaining = (lockout - datetime.now()).seconds // 60
    return remaining + 1

