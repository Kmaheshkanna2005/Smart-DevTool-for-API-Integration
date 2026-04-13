import requests
from bs4 import BeautifulSoup

def fetch_api_docs(url):
    print(f"Fetching documentation from: {url}...")
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extracting all headings (usually where endpoints are)
            headings = [h.text.strip() for h in soup.find_all(['h1', 'h2', 'h3'])]
            
            # Extracting all code snippets (usually where request bodies are)
            code_snippets = [code.text.strip() for code in soup.find_all('code')]
            
            return {
                "headings": headings[:10], # Just a sample for now
                "code_samples": code_snippets[:5]
            }
        else:
            return f"Error: Status code {response.status_code}"
    except Exception as e:
        return f"An error occurred: {e}"

if __name__ == "__main__":
    # Test with a sample API doc
    test_url = "https://jsonplaceholder.typicode.com/" 
    data = fetch_api_docs(test_url)
    print("Extracted Data:", data)