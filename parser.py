import os
import json
from openai import OpenAI
from dotenv import load_dotenv
import traceback

load_dotenv()

# Setup Groq Client
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

# Added 'url' to the function arguments so the prompt can use it!
def analyze_api_data(scraped_data, user_context, target_url):
    prompt = f"""
    Scraped Content: {scraped_data}
    Target URL: {target_url}
    Goal: {user_context}
    
    Instructions:
    
    you are best at reading the document and doing action 
    
    1. If the goal uses words like 'fetch', 'get', 'list', or 'show', use GET. 
    2. If the goal uses words like 'create', 'post', 'send', or 'add', use POST.
    3. IMPORTANT: If the user provides an ID but NO new data to change, it is a GET request.
    4. ONLY use POST/PUT if the user explicitly wants to save or change information.
    
    "CRITICAL: If the documentation does not explicitly show an 'Authorization' header as mandatory, set 'auth_type' to 'None' and 'auth_header_name' to null. Do not guess authentication."
    
    Return ONLY JSON:
    {{
        "base_url": "...",
        "endpoint": "...",
        "method": "POST or GET or PUT or DELETE or PATCH",
        "body_template": {{ "field1": "value", "field2": "value" }}, # Only if POST/PUT
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
        
        # Cleaning Markdown formatting if present
        if "```" in raw_content:
            raw_content = raw_content.split("```")[1]
            if raw_content.startswith("json"):
                raw_content = raw_content[4:].strip()
        
        return json.loads(raw_content)

    except json.JSONDecodeError:
        return {"error": f"AI returned invalid JSON: {raw_content}"}
    except Exception as e:
        traceback.print_exc() 
        return {"error": str(e)}

if __name__ == "__main__":
    # Test values
    sample_data = {'headings': ['GET /users'], 'code_samples': ["https://jsonplaceholder.typicode.com/users"]}
    context = "I want to fetch a single user by their ID."
    test_url = "https://jsonplaceholder.typicode.com"
    
    print("--- Starting Groq Analysis ---")
    # Pass all 3 arguments now!
    result = analyze_api_data(sample_data, context, test_url)
    print(json.dumps(result, indent=4))