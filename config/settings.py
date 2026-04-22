import streamlit as st

def configure_page():
    st.set_page_config(
        page_title="FactVerify Ai",
        page_icon="🔍",
        layout="wide",
        initial_sidebar_state="expanded"
    )

def get_firebase_config():
    if "firebase" not in st.secrets:
        st.error("Missing Firebase config in secrets")
        st.stop()
    return {
        "apiKey": st.secrets.firebase.api_key,
        "authDomain": st.secrets.firebase.auth_domain,
        "projectId": st.secrets.firebase.project_id,
    }

def get_groq_api_key():
    if "groq" not in st.secrets:
        raise Exception("Missing Groq API key in secrets")
    return st.secrets.groq.api_key


