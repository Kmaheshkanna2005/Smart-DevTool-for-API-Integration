import streamlit as st
import streamlit_authenticator as stauth
import json
import io
import os
import contextlib
from scraper import fetch_api_docs
from parser import analyze_api_data
from generator import generate_wrapper

# --- 1. DATA PERSISTENCE ---
USER_DATA_FILE = 'users.json'

def load_credentials():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, 'r') as f:
            return json.load(f)
    # Default admin if file is empty
    return {"usernames": {
        "admin": {"name": "Admin", "password": "abc", "email": "admin@test.com"}
    }}

def save_credentials():
    with open(USER_DATA_FILE, 'w') as f:
        json.dump(st.session_state['credentials'], f, indent=4)

if 'credentials' not in st.session_state:
    st.session_state['credentials'] = load_credentials()

# --- 2. AUTHENTICATOR SETUP ---
# Using a 32-character key to stop the HMAC warning
authenticator = stauth.Authenticate(
    st.session_state['credentials'],
    "api_integrator_cookie",
    "abcdefghijklmnopqrstuvwxyz123456", 
    cookie_expiry_days=30
)

# --- 3. PAGE CONFIG ---
st.set_page_config(page_title="Smart DevTool", page_icon="🚀", layout="centered")

# --- 4. AUTHENTICATION FLOW ---
if not st.session_state.get("authentication_status"):
    st.title("🔐 Smart DevTool Access")
    
    # Use a Radio button to toggle between Login and Register
    mode = st.radio("Choose Mode", ["Login", "Register"], horizontal=True)

    if mode == "Register":
        st.subheader("Create a New Account")
        # register_user now in a controlled flow
        try:
            # We catch the return values to check if someone ACTUALLY clicked submit
            res = authenticator.register_user(location='main')
            if res[0]: # email_of_registered_user is not None
                save_credentials()
                st.success('User registered successfully! Now switch to Login mode.')
        except Exception as e:
            st.error(f"Registration system error: {e}")

    elif mode == "Login":
        st.subheader("Welcome Back")
        try:
            # We only run login logic here
            authenticator.login(location='main')
        except Exception:
            # Silently handle the "User not authorized" during initial load
            pass

        if st.session_state.get("authentication_status") is False:
            st.error('Username/password is incorrect')
        elif st.session_state.get("authentication_status") is None:
            st.info('Please enter your details to continue.')

# --- 5. THE HOME PAGE (Only visible after Login) ---
if st.session_state.get("authentication_status"):
    
    # SIDEBAR SETUP
    with st.sidebar:
        st.header(f"Welcome, {st.session_state['name']}! 👋")
        # Logout button
        authenticator.logout('Logout', 'main')
        st.divider()
        st.header("Settings")
        lang_choice = st.selectbox("Language", ["python", "javascript", "java"])

    # MAIN CONTENT
    st.title("🚀 Smart DevTool: API Integrator")
    
    # Get API Key
    api_key = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")

    if not api_key:
        st.error("❌ Groq API Key missing! Check your secrets.")
    
    url = st.text_input("🔗 API Documentation URL")
    goal = st.text_area("🎯 What is your goal?")

    if st.button("Generate Wrapper Class", type="primary", use_container_width=True):
        if not url or not goal:
            st.warning("Please provide both URL and Goal.")
        else:
            with st.spinner("🤖 Analyzing documentation..."):
                try:
                    raw_data = fetch_api_docs(url)
                    metadata = analyze_api_data(raw_data, goal, url)
                    filename = generate_wrapper(metadata, lang_choice)
                    
                    with open(filename, "r", encoding="utf-8") as f:
                        st.session_state['generated_code'] = f.read()
                    st.session_state['lang'] = lang_choice
                except Exception as e:
                    st.error(f"Generation failed: {e}")

    # Code Display
    if 'generated_code' in st.session_state:
        st.divider()
        st.subheader(f"📄 Generated {st.session_state['lang'].capitalize()} Code")
        st.code(st.session_state['generated_code'], language=st.session_state['lang'])
        
        # Test Runner for Python
        if st.session_state['lang'] == "python":
            if st.button("▶️ Run & Test"):
                output_buffer = io.StringIO()
                try:
                    scope = {}
                    with contextlib.redirect_stdout(output_buffer):
                        exec(st.session_state['generated_code'], scope, scope)
                    st.success("Test complete.")
                    st.text_area("Console", value=output_buffer.getvalue(), height=200)
                except Exception as e:
                    st.error(f"Execution Error: {e}")