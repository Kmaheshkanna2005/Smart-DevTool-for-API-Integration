import streamlit as st
import json
import io
import os
import contextlib
from scraper import fetch_api_docs
from parser import analyze_api_data
from generator import generate_wrapper

# --- 1. API KEY SAFETY CHECK ---
# This ensures the app doesn't crash locally if secrets.toml is missing
api_key = None
try:
    if "GROQ_API_KEY" in st.secrets:
        api_key = st.secrets["GROQ_API_KEY"]
except Exception:
    # Fallback for local terminal environment variables
    api_key = os.getenv("GROQ_API_KEY")

# --- 2. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Smart DevTool | API Integrator", 
    page_icon="🚀", 
    layout="centered"
)

st.title("🚀 Smart DevTool: API Integrator")
st.markdown("Generate and test API wrappers in seconds using AI.")

# --- 3. SIDEBAR SETTINGS ---
with st.sidebar:
    st.header("⚙️ Configuration")
    lang_choice = st.selectbox(
        "Target Language", 
        ["python", "javascript", "java"],
        help="Select the programming language for the generated wrapper."
    )
    
    st.divider()
    
    # Connection Status Indicator
    if api_key:
        st.success("Groq AI Engine: Connected ✅")
    else:
        st.error("Groq AI Engine: Disconnected ❌")
        st.info("💡 To fix: Add `GROQ_API_KEY` to `.streamlit/secrets.toml` locally or to 'Secrets' on Streamlit Cloud.")

    st.info("ℹ️ Live execution is currently only supported for Python wrappers.")

# --- 4. USER INPUTS ---
url = st.text_input("🔗 API Documentation URL", placeholder="https://api.example.com/docs")
goal = st.text_area("🎯 What is your goal?", placeholder="e.g., Get the 7-day weather forecast for Coimbatore")

with st.expander("🔐 Authentication (Optional)"):
    col1, col2 = st.columns(2)
    with col1:
        auth_method = st.selectbox("Auth Type", ["None", "API-Key", "Bearer"])
    with col2:
        user_token = st.text_input("Token / Key", type="password", placeholder="Paste your token here")

# --- 5. CORE LOGIC: GENERATION ---
if st.button("Generate Wrapper Class", type="primary", use_container_width=True):
    if not api_key:
        st.error("Operation failed: Missing Groq API Key.")
    elif not url or not goal:
        st.error("Please provide both the Documentation URL and your Goal!")
    else:
        with st.spinner("🤖 AI is analyzing documentation and writing code..."):
            try:
                # Step 1: Scrape the webpage
                raw_data = fetch_api_docs(url)
                
                # Step 2: Parse using AI (Passes data to Groq via parser.py)
                metadata = analyze_api_data(raw_data, goal, url)
                
                if "error" in metadata:
                    st.error(f"AI Parsing Error: {metadata['error']}")
                else:
                    # Step 3: Generate the code file
                    filename = generate_wrapper(
                        metadata, 
                        language=lang_choice, 
                        user_token=user_token,
                        auth_method=auth_method
                    )
                    
                    # Store results in session state to survive page refreshes
                    with open(filename, "r", encoding="utf-8") as f:
                        st.session_state['generated_code'] = f.read()
                    st.session_state['lang'] = lang_choice
                    st.success(f"✨ {lang_choice.capitalize()} wrapper generated successfully!")
                
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")

# --- 6. DISPLAY & EXECUTION SECTION ---
if 'generated_code' in st.session_state:
    st.divider()
    st.subheader(f"📄 Generated {st.session_state['lang'].capitalize()} Code")
    st.code(st.session_state['generated_code'], language=st.session_state['lang'])

    # Execution is only for Python
    if st.session_state['lang'] == "python":
        if st.button("▶️ Run & Test This Code", use_container_width=True):
            st.write("🛰️ **Sending Request to API...**")
            
            output_buffer = io.StringIO()
            try:
                # CRITICAL: We use a shared dictionary for globals/locals 
                # to ensure class definitions and execution share memory.
                exec_scope = {}
                
                with contextlib.redirect_stdout(output_buffer):
                    exec(st.session_state['generated_code'], exec_scope, exec_scope)
                
                result_text = output_buffer.getvalue()
                
                st.subheader("🖥️ Execution Output")
                if result_text.strip():
                    st.success("API Call Processed.")
                    st.text_area("Console Output", value=result_text, height=350)
                else:
                    st.warning("The code executed but returned no output to the console.")
                    st.info("💡 Hint: Ensure your generated code contains 'print()' statements.")
                    
            except Exception as e:
                st.error(f"Runtime Execution Error: {e}")