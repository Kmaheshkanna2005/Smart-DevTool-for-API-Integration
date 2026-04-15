import streamlit as st
import json
import io
import contextlib
from scraper import fetch_api_docs
from parser import analyze_api_data
from generator import generate_wrapper

st.set_page_config(page_title="Smart DevTool", page_icon="🚀")

st.title("🚀 Smart DevTool: API Integrator")

# --- Sidebar ---
with st.sidebar:
    st.header("Settings")
    # Note: Execution currently only works for Python
    lang_choice = st.selectbox("Preferred Language", ["python", "javascript"])
    st.info("Live execution is only available for Python.")

# --- Inputs ---
url = st.text_input("🔗 API Documentation URL")
goal = st.text_area("🎯 What is your goal?")

st.subheader("Authentication (Optional)")
user_token = st.text_input("Paste your Session Token/Bearer Token here:", type="password")
auth_method = st.selectbox("Auth Type", ["None", "API-Key"])

if st.button("Generate Wrapper Class"):
    if not url or not goal:
        st.error("Missing inputs!")
    else:
        # Step 1 & 2: Scrape and Parse
        raw_data = fetch_api_docs(url)
        metadata = analyze_api_data(raw_data, goal, url)
        
        # Step 3: Generate and Store in Session State
        filename = generate_wrapper(
        metadata, 
        language=lang_choice, 
        user_token=user_token,  # Pass the new token
        auth_method=auth_method # Pass the new method
)
        with open(filename, "r") as f:
            st.session_state['generated_code'] = f.read()
        st.session_state['lang'] = lang_choice

# --- Display & Execute Section ---
if 'generated_code' in st.session_state:
    st.divider()
    st.subheader(f"📄 Generated {st.session_state['lang'].capitalize()} Code")
    st.code(st.session_state['generated_code'], language=st.session_state['lang'])

    # Only show "Run" button if language is Python
    if st.session_state['lang'] == "python":
        if st.button("▶️ Run Generated Code"):
            st.write("🛰️ **Executing API Request...**")
            
            # This captures the 'print()' output from the executed code
            output_buffer = io.StringIO()
            try:
                with contextlib.redirect_stdout(output_buffer):
                    # Execute the code
                    # Note: exec() runs the code in the current environment
                    exec(st.session_state['generated_code'])
                
                # Show the output
                st.subheader("🖥️ Execution Output")
                result = output_buffer.getvalue()
                if result:
                    st.success("API Call Successful!")
                    st.text_area("Terminal Output", value=result, height=200)
                else:
                    st.warning("Code executed but returned no output.")
                    
            except Exception as e:
                st.error(f"Execution Error: {e}")