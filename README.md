
# Smart API Integrator: AI-Driven Wrapper Generator

**Smart API Integrator** is an intelligent developer tool that bridges the gap between static API documentation and functional code. By providing a documentation URL and a natural language goal, the tool scrapes the site, parses the schema using AI, and auto-generates ready-to-use API wrapper classes in **Python**, **JavaScript**, and **Java**.

## 🚀 Setup Instructions

### 1. Prerequisites
* **Python 3.8+**
* **GROQ API Key** (Required for the AI Parsing logic)
* **Node.js** (Optional, to run generated JavaScript)
* **Java 11+** (Optional, to compile generated Java code)

### 2. Installation
Clone the repository and install the necessary Python libraries:

```bash
# Clone the repo
git clone https://github.com/Kmaheshkanna2005/Smart-API-Integrator.git
cd Smart-API-Integrator

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration
Create a `.env` file in the root directory or enter your key directly into the Streamlit sidebar:
```text
GROQ_API_KEY=your_actual_key_here
```

### 4. Running the App
```bash
streamlit run app.py
```

---

## 🛠 Usage
1.  **Enter URL:** Paste a link to any API documentation (e.g., Open-Meteo or ReqRes).
2.  **Define Goal:** State what you want to do (e.g., "I want to get the 7-day weather forecast").
3.  **Select Language:** Choose between Python, JavaScript, or Java.
4.  **Generate:** The tool will scrape the docs, identify the endpoint, and generate a `.py`, `.js`, or `.java` file.
5.  **Test:** Use the generated code immediately to make live API calls.

---

## 📦 Dependencies
* **Streamlit:** For the web-based user interface.
* **GROQ Generative AI:** To parse unstructured HTML into structured API metadata.
* **BeautifulSoup4:** For web scraping documentation content.
* **Requests:** For handling Python-based API communication and testing.

---

### 🔐 Security & Persistence 
* **Stateful Authentication:** Integrated a secure Login and Registration system to protect engine access.
* **Data Persistence:** Implemented a JSON-based storage layer to maintain user credentials across application restarts.
* **Secret Abstraction:** Utilizes .gitignore and Streamlit Secrets to prevent API key leakage.

---

## 💡 Solution Approach

My approach focuses on **Dynamic Metadata Mapping**. Instead of hard-coding support for specific APIs, the system follows a three-stage pipeline:

### 1. Extraction & Cleaning
The tool scrapes the documentation URL and strips away unnecessary HTML tags (scripts, styles) to keep only the relevant text and table data, ensuring the AI doesn't hit token limits.

### 2. AI Schema Inference
I use an LLM (GROQ) to act as a "Technical Architect." It analyzes the scraped text to find:
* The **Base URL** and specific **Endpoint**.
* The required **HTTP Method** (GET/POST/PUT/DELETE).
* The **Authentication Strategy** (Bearer, API-Key, or Public).

### 3. Polyglot Template Injection
The final step uses a custom-built **Code Generation Engine**. It takes the JSON metadata from the AI and injects it into language-specific templates. 
* **Python:** Uses the `requests` library with robust error handling.
* **JavaScript:** Uses the modern `fetch` API compatible with Node.js.
* **Java:** Uses the native `java.net.http.HttpClient` to avoid external dependency overhead.



---

## 📈 Roadmap
- [x] Phase 1: Research & Scraper Logic
- [x] Phase 2: AI Parsing & Metadata Extraction
- [x] Phase 3: Multi-language Code Generation (Python, JS, Java)
- [x] Phase 4: Error Handling for Timeouts and 405/403 errors
- [x] Phase 5: Integrated User Authentication (Login/Register)
- [x] Phase 6: Persistent JSON-based User Storage

---

**Author:** Mahesh Kanna  
**License:** MIT