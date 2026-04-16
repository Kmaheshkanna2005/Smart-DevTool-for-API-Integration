import os
import json
import traceback
import streamlit as st
from openai import OpenAI

# Initialize Groq Client using Streamlit Secrets
# This replaces os.getenv and load_dotenv()
def get_groq_client():
    try:
        # Check if we are running locally or on Streamlit Cloud
        if "GROQ_API_KEY" in st.secrets:
            api_key = st.secrets["GROQ_API_KEY"]
        else:
            # Fallback for local testing if secrets.toml isn't set up
            api_key = os.getenv("GROQ_API_KEY")
            
        return OpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1"
        )
    except Exception as e:
        st.error("Groq API Key not found. Please set it in Streamlit Secrets.")
        return None

def analyze_api_data(scraped_data, user_context, target_url):
    client = get_groq_client()
    if not client:
        return {"error": "API Client not initialized"}

    prompt = f"""
    Scraped Content: {scraped_data}
    Target URL: {target_url}
    Goal: {user_context}
    
    Instructions:
    1. Identify the base_url and endpoint from the content.
    2. Method Selection:
       - Use GET for 'fetch', 'list', 'show', or 'read'.
       - Use POST for 'create', 'add', or 'send'.
       - If an ID is provided but no data payload is mentioned, default to GET.
    3. Authentication Detection:
       - If the documentation explicitly mentions 'Authorization', 'Bearer', or 'x-api-key', identify the 'auth_type' (Bearer or API-Key).
       - If no auth is mentioned, set 'auth_type' to 'None' and 'auth_header_name' to null.
    
    Return ONLY valid JSON:
    {{
        "base_url": "...",
        "endpoint": "...",
        "method": "...",
        "body_template": {{}}, 
        "auth_type": "None",
        "auth_header_name": "Authorization"
    }}
    """

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a specialized JSON generator. Never speak, only output JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )
        
        raw_content = response.choices[0].message.content.strip()
        
        # Cleaning Markdown formatting
        if "```" in raw_content:
            raw_content = raw_content.split("```")[1]
            if raw_content.startswith("json"):
                raw_content = raw_content[4:].strip()
        
        return json.loads(raw_content)

    except json.JSONDecodeError:
        return {"error": "AI returned invalid JSON format."}
    except Exception as e:
        traceback.print_exc() 
        return {"error": str(e)}

# Test block
if __name__ == "__main__":
    sample_data = "GET /users https://jsonplaceholder.typicode.com/users"
    context = "I want to fetch all users."
    test_url = "https://jsonplaceholder.typicode.com"
    
    print("--- Starting Groq Analysis ---")
    result = analyze_api_data(sample_data, context, test_url)
    print(json.dumps(result, indent=4))