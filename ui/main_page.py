import streamlit as st
from api.groq_client import get_verified_response
from utils.helpers import get_greeting, get_display_name, random_message

FEEDBACK_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdlh_ogw2I3hByMMGTJRFtWwAzKWklAAzFvO7g7ApinQ6jaSw/viewform"


def show_main_app():
    first_name = st.session_state.get("first_name", "")
    last_name = st.session_state.get("last_name", "")
    email = st.session_state.get("email", "")

    display_name = get_display_name(first_name, last_name, email)
    greeting = get_greeting()
    message = random_message()

    _render_header(display_name, greeting, message)
    _render_sidebar()
    _render_query_form()


def _render_header(display_name, greeting, message):
    col1, col2 = st.columns([5, 1])
    with col1:
        st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 2rem;">
                <div class="user-avatar">{display_name[0].upper()}</div>
                <div>
                    <h1 style="margin: 0; color: var(--text); font-size: 1.8rem;">{greeting}, {display_name}</h1>
                    <p style="margin: 0; color: var(--text-secondary); font-size: 1.1rem;">{message}</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        if st.button("Logout", use_container_width=True, key="logout_btn"):
            st.session_state.clear()
            st.rerun()


def _render_sidebar():
    with st.sidebar:
        st.markdown("""
            <div class="feedback-container">
                <h3 style="color: var(--primary);">Help Us Improve</h3>
                <p style="color: var(--text-secondary); font-size: 0.9rem; line-height: 1.5;">
                    Share your thoughts, suggest improvements, or report issues.
                </p>
            </div>
        """, unsafe_allow_html=True)
        st.markdown(f'<a href="{FEEDBACK_URL}" target="_blank" class="link-button">Share Your Feedback</a>', unsafe_allow_html=True)


def _render_query_form():
    with st.form("query_form"):
        st.markdown("<h2 style='color: var(--text); margin-bottom: 1rem;'>Research Query</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color: var(--text-secondary); margin-bottom: 1.5rem;'>Enter your question or statement to verify with academic sources</p>", unsafe_allow_html=True)

        prompt = st.text_area(
            "Query",
            placeholder="Example: 'What is the current scientific consensus on climate change?'",
            height=200,
            key="query_input",
            label_visibility="collapsed",
        )

        if st.form_submit_button("Verify Information", use_container_width=True, type="primary"):
            if not prompt:
                st.warning("Please enter a question")
            else:
                with st.spinner("🔍 Verifying with academic databases..."):
                    response, sources = get_verified_response(prompt)

                if response:
                    st.markdown(f"""
                        <div class="response-card">
                            <p style="color: var(--text); font-size: 1.1rem; line-height: 1.6;">{response}</p>
                        </div>
                    """, unsafe_allow_html=True)

                    if sources:
                        st.markdown("<h3 style='color: var(--text-secondary); margin: 2rem 0 1rem;'>📚 Verified Sources:</h3>", unsafe_allow_html=True)
                        for source in sources:
                            st.markdown(f'<div class="source-item"><p style="margin: 0; color: var(--text);">{source}</p></div>', unsafe_allow_html=True)
                else:
                    st.error("Failed to get a response.")
                    for err in sources:
                        st.error(err)
