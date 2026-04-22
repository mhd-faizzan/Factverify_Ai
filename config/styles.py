import streamlit as st

_CSS = """
<style>
    :root {
        --primary: #4A6FA5;
        --primary-hover: #3A5A8C;
        --bg: #0E1117;
        --card-bg: #1E293B;
        --text: #F8FAFC;
        --text-secondary: #94A3B8;
        --border: #334155;
    }

    .stApp {
        background-color: var(--bg) !important;
        color: var(--text) !important;
        max-width: 1200px !important;
        margin: 0 auto !important;
    }

    .header-container {
        text-align: center;
        margin-bottom: 3rem;
        padding-top: 1rem;
    }

    .auth-container {
        max-width: 500px;
        margin: 0 auto;
        padding: 2rem 0;
    }

    .auth-card {
        background: var(--card-bg);
        border-radius: 12px;
        padding: 2.5rem;
        border: 1px solid var(--border);
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
    }

    .stTextInput input,
    .stTextArea textarea {
        background: #1E293B !important;
        border: 1px solid var(--border) !important;
        color: var(--text) !important;
        padding: 12px !important;
        border-radius: 8px !important;
    }

    .stButton button {
        background: var(--primary) !important;
        color: white !important;
        border: none !important;
        padding: 12px 24px !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
    }

    .stButton button:hover {
        background: var(--primary-hover) !important;
        transform: translateY(-1px);
    }

    .stTabs [data-baseweb="tab"] {
        padding: 12px 24px;
        border-radius: 8px;
    }

    .stTabs [aria-selected="true"] {
        background: var(--primary) !important;
        color: white !important;
    }

    .source-item {
        padding: 1rem;
        margin: 0.75rem 0;
        background: #334155;
        border-radius: 8px;
        border-left: 4px solid var(--primary);
        transition: transform 0.2s ease;
    }

    .source-item:hover { transform: translateX(4px); }

    .user-avatar {
        width: 56px;
        height: 56px;
        border-radius: 50%;
        background: linear-gradient(135deg, var(--primary), #6B46C1);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        font-size: 1.4rem;
        margin-right: 1rem;
    }

    .response-card {
        margin-top: 2rem;
        padding: 1.5rem;
        background: #334155;
        border-radius: 10px;
        border-left: 4px solid var(--primary);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }

    section[data-testid="stSidebar"] {
        background-color: var(--card-bg) !important;
        border-right: 1px solid var(--border) !important;
    }

    .feedback-container {
        padding: 1.5rem;
        margin-bottom: 2rem;
    }

    .link-button {
        display: inline-block;
        background: var(--primary);
        color: white !important;
        padding: 12px 24px;
        border-radius: 8px;
        text-align: center;
        text-decoration: none;
        font-weight: 500;
        width: 100%;
        transition: all 0.2s ease;
    }

    .link-button:hover {
        background: var(--primary-hover);
        transform: translateY(-1px);
        color: white;
    }
</style>
"""


def inject_styles():
    st.markdown(_CSS, unsafe_allow_html=True)
