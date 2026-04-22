import streamlit as st
from auth.firebase import handle_login, handle_signup
from auth.session import (
    is_locked_out, record_failed_attempt, reset_attempts,
    set_token, validate_password, lockout_remaining
)


def show_auth_ui():
    st.markdown("""
        <div class="header-container">
            <h1 style="color: var(--primary); font-size: 2.5rem; margin-bottom: 0.5rem;">🔍 FactVerify Ai</h1>
            <p style="color: var(--text-secondary); font-size: 1.1rem;">Academic-grade fact verification at your fingertips</p>
        </div>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown("<div class='auth-container'>", unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        with tab1:
            _login_form()
        with tab2:
            _signup_form()
        st.markdown("</div>", unsafe_allow_html=True)


def _login_form():
    st.markdown("<div class='auth-card'>", unsafe_allow_html=True)
    with st.form("login_form"):
        st.markdown("<h3 style='color: var(--text); margin-bottom: 1.5rem;'>Welcome back</h3>", unsafe_allow_html=True)
        email = st.text_input("Email", placeholder="your@email.com", key="login_email")
        password = st.text_input("Password", type="password", key="login_pass")

        if st.form_submit_button("Login", use_container_width=True):
            if not email or not password:
                st.error("Please fill all fields.")
                return

            if is_locked_out():
                mins = lockout_remaining()
                st.error(f"Too many failed attempts. Try again in {mins} minute(s).")
                return

            success, message, result = handle_login(email, password)

            if success:
                reset_attempts()
                set_token(result["idToken"])
                st.session_state.update({
                    "logged_in": True,
                    "email": email,
                    "first_name": result["first_name"],
                    "last_name": result["last_name"],
                })
                st.rerun()
            else:
                record_failed_attempt()
                attempts_left = 5 - st.session_state.get("login_attempts", 0)
                if attempts_left > 0:
                    st.error(f"{message} {attempts_left} attempt(s) remaining.")
                else:
                    st.error("Account locked for 15 minutes due to too many failed attempts.")

    st.markdown("</div>", unsafe_allow_html=True)


def _signup_form():
    st.markdown("<div class='auth-card'>", unsafe_allow_html=True)
    with st.form("signup_form"):
        st.markdown("<h3 style='color: var(--text); margin-bottom: 1.5rem;'>Create an account</h3>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            first_name = st.text_input("First Name", placeholder="Given Name", key="signup_fname")
        with col2:
            last_name = st.text_input("Last Name", placeholder="Family Name", key="signup_lname")

        email = st.text_input("Email", placeholder="your@email.com", key="signup_email")

        col3, col4 = st.columns(2)
        with col3:
            password = st.text_input("Password", type="password", key="signup_pass")
        with col4:
            confirm = st.text_input("Confirm Password", type="password", key="signup_cpass")

        st.caption("8+ characters, one uppercase letter, one number.")

        if st.form_submit_button("Create Account", use_container_width=True):
            if not all([first_name, last_name, email, password, confirm]):
                st.error("Please fill all fields.")
            elif password != confirm:
                st.error("Passwords don't match.")
            else:
                pw_error = validate_password(password)
                if pw_error:
                    st.error(pw_error)
                else:
                    success, message, result = handle_signup(first_name, last_name, email, password)
                    if success:
                        set_token(result["idToken"])
                        st.session_state.update({
                            "logged_in": True,
                            "email": email,
                            "first_name": first_name,
                            "last_name": last_name,
                        })
                        st.rerun()
                    else:
                        st.error(message)

    st.markdown("</div>", unsafe_allow_html=True)


