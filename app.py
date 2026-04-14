import streamlit as st
import requests
from datetime import datetime
import random
from groq import Groq

# ======================
# CONFIG
# ======================
st.set_page_config(
    page_title="FactVerify AI",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
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
        .header-container { text-align: center; margin-bottom: 3rem; padding-top: 1rem; }
        .auth-container { max-width: 500px; margin: 0 auto; padding: 2rem 0; }
        .auth-card {
            background: var(--card-bg); border-radius: 12px; padding: 2.5rem;
            border: 1px solid var(--border); box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
        }
        .stTextInput input, .stTextArea textarea {
            background: #1E293B !important; border: 1px solid var(--border) !important;
            color: var(--text) !important; padding: 12px !important; border-radius: 8px !important;
        }
        .stButton button {
            background: var(--primary) !important; color: white !important;
            border: none !important; padding: 12px 24px !important;
            border-radius: 8px !important; font-weight: 500 !important;
            transition: all 0.2s ease !important;
        }
        .stButton button:hover {
            background: var(--primary-hover) !important;
            transform: translateY(-1px);
        }
        .stTabs [data-baseweb="tab"] { padding: 12px 24px; border-radius: 8px; }
        .stTabs [aria-selected="true"] { background: var(--primary) !important; color: white !important; }
        .source-item {
            padding: 1rem; margin: 0.75rem 0; background: #334155;
            border-radius: 8px; border-left: 4px solid var(--primary);
            transition: transform 0.2s ease;
        }
        .source-item:hover { transform: translateX(4px); }
        .user-avatar {
            width: 56px; height: 56px; border-radius: 50%;
            background: linear-gradient(135deg, var(--primary), #6B46C1);
            display: flex; align-items: center; justify-content: center;
            color: white; font-weight: bold; font-size: 1.4rem; margin-right: 1rem;
        }
        .response-card {
            margin-top: 2rem; padding: 1.5rem; background: #334155;
            border-radius: 10px; border-left: 4px solid var(--primary);
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        section[data-testid="stSidebar"] {
            background-color: var(--card-bg) !important;
            border-right: 1px solid var(--border) !important;
        }
        .link-button {
            display: inline-block; background: var(--primary); color: white !important;
            padding: 12px 24px; border-radius: 8px; text-align: center;
            text-decoration: none; font-weight: 500; width: 100%;
            transition: all 0.2s ease;
        }
        .link-button:hover {
            background: var(--primary-hover);
            transform: translateY(-1px);
            color: white;
        }
    </style>
""", unsafe_allow_html=True)

# ======================
# SESSION STATE
# ======================
if 'logged_in' not in st.session_state:
    st.session_state.update({
        'logged_in': False,
        'email': "",
        'first_name': "",
        'last_name': "",
        'id_token': ""
    })

# ======================
# FIREBASE
# ======================
def initialize_firebase():
    if "firebase" not in st.secrets:
        st.error("Missing Firebase configuration in secrets.")
        st.stop()
    return {
        "apiKey": st.secrets.firebase.api_key,
        "authDomain": st.secrets.firebase.auth_domain,
        "projectId": st.secrets.firebase.project_id
    }

firebase_config = initialize_firebase()
FIREBASE_SIGNUP_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={firebase_config['apiKey']}"
FIREBASE_LOGIN_URL  = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={firebase_config['apiKey']}"

def handle_signup(first_name, last_name, email, password):
    try:
        res = requests.post(FIREBASE_SIGNUP_URL,
            json={"email": email, "password": password, "returnSecureToken": True}, timeout=10)
        if res.status_code == 200:
            id_token = res.json().get("idToken", "")
            requests.post(
                f"https://identitytoolkit.googleapis.com/v1/accounts:update?key={firebase_config['apiKey']}",
                json={"idToken": id_token, "displayName": f"{first_name} {last_name}", "returnSecureToken": True},
                timeout=10
            )
            return True, "Account created successfully!", {"idToken": id_token, "first_name": first_name, "last_name": last_name}
        return False, res.json().get("error", {}).get("message", "Unknown error"), None
    except Exception as e:
        return False, f"Connection error: {str(e)}", None

def handle_login(email, password):
    try:
        res = requests.post(FIREBASE_LOGIN_URL,
            json={"email": email, "password": password, "returnSecureToken": True}, timeout=10)
        if res.status_code == 200:
            id_token = res.json().get("idToken", "")
            user_info = requests.post(
                f"https://identitytoolkit.googleapis.com/v1/accounts:lookup?key={firebase_config['apiKey']}",
                json={"idToken": id_token}, timeout=10
            )
            user_data = user_info.json().get("users", [{}])[0]
            names = user_data.get("displayName", "").split() if user_data.get("displayName") else []
            return True, "Login successful!", {
                "idToken": id_token,
                "first_name": names[0] if names else "",
                "last_name": names[-1] if len(names) > 1 else ""
            }
        return False, res.json().get("error", {}).get("message", "Unknown error"), None
    except Exception as e:
        return False, f"Connection error: {str(e)}", None

# ======================
# GROQ LLM
# ======================
def get_verified_response(prompt):
    try:
        if "groq" not in st.secrets:
            raise Exception("Missing Groq API configuration in secrets")

        client = Groq(api_key=st.secrets.groq.api_key)

        system_prompt = f"""You are a senior academic researcher and fact-checker. Your task is to:
1. Provide accurate, well-researched information current to {datetime.now().strftime('%B %Y')}
2. Verify claims with evidence-based reasoning
3. Cite 3-5 reliable academic sources
4. Be transparent about limitations or uncertainties

Format your response as:
- Clear, factual answer
- Evidence and reasoning
- Sources section with format: [Title](URL) - Author (Year) or DOI:...

Separate your main response from sources using ###SOURCES### as a divider."""

        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=2000,
            top_p=0.9,
            stream=True
        )

        full_response = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                full_response += chunk.choices[0].delta.content

        if "###SOURCES###" in full_response:
            parts = full_response.split("###SOURCES###")
            sources = [s.strip() for s in parts[1].strip().split("\n") if s.strip()]
            return parts[0].strip(), sources

        return full_response.strip(), []

    except Exception as e:
        return None, [f"Groq API Error: {str(e)}"]

# ======================
# AUTH UI
# ======================
def show_auth_ui():
    st.markdown("""
        <div class="header-container">
            <h1 style="color: var(--primary); font-size: 2.5rem; margin-bottom: 0.5rem;">🔍 FactVerify AI</h1>
            <p style="color: var(--text-secondary); font-size: 1.1rem;">Academic-grade fact verification at your fingertips</p>
        </div>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown("<div class='auth-container'>", unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["Login", "Sign Up"])

        with tab1:
            st.markdown("<div class='auth-card'>", unsafe_allow_html=True)
            with st.form("login_form"):
                st.markdown("<h3 style='color: var(--text); margin-bottom: 1.5rem;'>Welcome back</h3>", unsafe_allow_html=True)
                email    = st.text_input("Email", placeholder="your@email.com", key="login_email")
                password = st.text_input("Password", type="password", key="login_pass")
                if st.form_submit_button("Login", use_container_width=True):
                    if email and password:
                        success, message, result = handle_login(email, password)
                        if success:
                            st.session_state.update({
                                'logged_in': True, 'email': email,
                                'id_token': result.get("idToken", ""),
                                'first_name': result.get("first_name", ""),
                                'last_name': result.get("last_name", "")
                            })
                            st.rerun()
                        else:
                            st.error(message)
                    else:
                        st.error("Please fill all fields")
            st.markdown("</div>", unsafe_allow_html=True)

        with tab2:
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
                    confirm_pass = st.text_input("Confirm Password", type="password", key="signup_cpass")
                if st.form_submit_button("Create Account", use_container_width=True):
                    if not all([first_name, last_name, email, password, confirm_pass]):
                        st.error("Please fill all fields")
                    elif password != confirm_pass:
                        st.error("Passwords don't match")
                    else:
                        success, message, result = handle_signup(first_name, last_name, email, password)
                        if success:
                            st.session_state.update({
                                'logged_in': True, 'email': email,
                                'first_name': first_name, 'last_name': last_name,
                                'id_token': result.get("idToken", "")
                            })
                            st.rerun()
                        else:
                            st.error(message)
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

# ======================
# MAIN APP UI
# ======================
def show_main_app():
    first_name   = st.session_state.get('first_name', '')
    last_name    = st.session_state.get('last_name', '')
    display_name = f"{first_name[0].upper()}. {last_name}" if first_name else st.session_state.email.split('@')[0]

    hour = datetime.now().hour
    greeting = "Good Morning" if 5 <= hour < 12 else "Good Afternoon" if hour < 17 else "Good Evening"

    messages = [
        "What fact shall we verify today?",
        "Ready to uncover the truth?",
        "Knowledge is power — let's find some!",
        "Every search brings us closer to truth.",
        "Let's explore something fascinating!"
    ]

    col1, col2 = st.columns([5, 1])
    with col1:
        st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 2rem;">
                <div class="user-avatar">{display_name[0].upper()}</div>
                <div>
                    <h1 style="margin: 0; color: var(--text); font-size: 1.8rem;">{greeting}, {display_name}</h1>
                    <p style="margin: 0; color: var(--text-secondary); font-size: 1.1rem;">{random.choice(messages)}</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        if st.button("Logout", use_container_width=True, key="logout_btn"):
            st.session_state.clear()
            st.rerun()

    with st.sidebar:
        st.markdown("""
            <div style="padding: 1.5rem;">
                <h3 style="color: #4A6FA5; margin-top: 0;">Help Us Improve</h3>
                <p style="color: #94A3B8; font-size: 0.9rem; line-height: 1.5;">
                    Your feedback helps us enhance FactVerify AI. Share thoughts, suggest improvements, or report issues.
                </p>
            </div>
        """, unsafe_allow_html=True)
        st.markdown("""
            <a href="https://docs.google.com/forms/d/e/1FAIpQLSdlh_ogw2I3hByMMGTJRFtWwAzKWklAAzFvO7g7ApinQ6jaSw/viewform"
               target="_blank" class="link-button">Share Your Feedback</a>
        """, unsafe_allow_html=True)

    with st.form("query_form"):
        st.markdown("<h2 style='color: var(--text); margin-bottom: 0.5rem;'>Research Query</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color: var(--text-secondary); margin-bottom: 1.5rem;'>Enter your question or claim to verify with academic sources</p>", unsafe_allow_html=True)

        prompt = st.text_area(
            "Query", placeholder="Example: 'What is the current scientific consensus on climate change?'",
            height=200, key="query_input", label_visibility="collapsed"
        )

        if st.form_submit_button("Verify Information", use_container_width=True, type="primary"):
            if not prompt:
                st.warning("Please enter a question.")
            else:
                with st.spinner("🔍 Verifying with academic sources..."):
                    response, sources = get_verified_response(prompt)

                if response:
                    st.markdown(f"""
                        <div class="response-card">
                            <p style="color: var(--text); font-size: 1.1rem; line-height: 1.6;">{response}</p>
                        </div>
                    """, unsafe_allow_html=True)
                    if sources:
                        st.markdown("<h3 style='color: var(--text-secondary); margin-top: 2rem;'>📚 Verified Sources</h3>", unsafe_allow_html=True)
                        for source in sources:
                            st.markdown(f"""
                                <div class="source-item">
                                    <p style="margin: 0; color: var(--text); font-size: 1rem;">{source}</p>
                                </div>
                            """, unsafe_allow_html=True)
                else:
                    st.error("Failed to get a response. Please check:")
                    for err in sources:
                        st.error(err)

# ======================
# ROUTING
# ======================
if not st.session_state.logged_in:
    show_auth_ui()
else:
    show_main_app()
