import os
import json
from google import genai
from dotenv import load_dotenv

# Load API Key from .env
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY not found. Please check your .env file.")

# Initialize the modern client
client = genai.Client(api_key=API_KEY)

def analyze_api_data(scraped_data, user_context):
    """
    Takes raw scraped text and converts it into a structured technical map
    using Gemini 2.0 Flash.
    """
    prompt = f"""
    SYSTEM: You are a Senior Backend Engineer. Your task is to extract API integration details.
    
    DATA FROM DOCS:
    {scraped_data}
    
    DEVELOPER'S GOAL:
    {user_context}
    
    INSTRUCTIONS:
    Identify the technical details needed to achieve the goal. 
    Return ONLY a valid JSON object with these keys:
    - base_url: (The root API URL)
    - endpoint: (The specific path)
    - method: (GET, POST, etc.)
    - parameters: (List of keys required in the body or query)
    - auth_type: (e.g., 'none', 'api_key', 'bearer_token')
    
    JSON ONLY. NO MARKDOWN. NO EXPLANATION.
    """

    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash', 
            contents=prompt
        )
        
        # Clean the response text (remove ```json wrappers if AI adds them)
        clean_json = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(clean_json)
        
    except Exception as e:
        return {"error": f"AI Analysis failed: {str(e)}"}

if __name__ == "__main__":
    # This simulates the data we got from scraper.py
    sample_scraped_data = {
        'headings': ['Resources', 'Routes', 'GET /posts'], 
        'code_samples': ["fetch('[https://jsonplaceholder.typicode.com/posts](https://jsonplaceholder.typicode.com/posts)')"]
    }
    
    user_intent = "I want to create a new blog post."
    
    print("--- Starting AI Analysis ---")
    result = analyze_api_data(sample_scraped_data, user_intent)
    print(json.dumps(result, indent=4))