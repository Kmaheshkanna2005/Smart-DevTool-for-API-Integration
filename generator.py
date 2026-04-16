import os
import json

def generate_wrapper(api_metadata, language="python", user_token=None, auth_method="None"):
    # 1. Setup metadata variables
    base_url = api_metadata.get("base_url", "").rstrip("/")
    endpoint = api_metadata.get("endpoint", "")
    if not endpoint.startswith("/"):
        endpoint = "/" + endpoint
        
    method = api_metadata.get("method", "GET").upper()
    
    auth_type = auth_method if user_token and auth_method != "None" else api_metadata.get("auth_type", "None")
    header_name = api_metadata.get("auth_header_name", "Authorization")
    body_template = api_metadata.get("body_template", {})

    if language.lower() == "javascript":
        code = f"""
class ApiClient {{
    constructor(apiKey = null) {{
        this.baseUrl = "{base_url}";
        this.apiKey = apiKey;
        this.headers = {{ 
            "Content-Type": "application/json",
            "User-Agent": "Node-Fetch-Client"
        }};
        
        if (this.apiKey && "{auth_type}" !== "None") {{
            this.headers["{header_name}"] = "{auth_type}" === "Bearer" ? `Bearer ${{this.apiKey}}` : this.apiKey;
        }}
    }}

    async callApi(data = null, userId = null, params = null) {{
        let currentEndpoint = "{endpoint}";
        
        if (userId) {{
            currentEndpoint = currentEndpoint.includes("{{user_id}}") 
                ? currentEndpoint.replace("{{user_id}}", userId) 
                : `${{currentEndpoint.replace(/\\/+$/, "")}}/${{userId}}`;
        }}

        const url = new URL(`${{this.baseUrl}}${{currentEndpoint}}`);
        if (params) {{
            Object.keys(params).forEach(key => url.searchParams.append(key, params[key]));
        }}

        console.log(`\\n--- Making {method} request to: ${{url.toString()}} ---`);

        try {{
            const response = await fetch(url, {{
                method: "{method}",
                headers: this.headers,
                body: "{method}" !== "GET" ? JSON.stringify(data) : null
            }});

            if (!response.ok) {{
                const errorText = await response.text();
                return {{ error: `HTTP ${{response.status}}`, details: errorText }};
            }}

            const contentType = response.headers.get("content-type");
            if (contentType && contentType.includes("application/json")) {{
                return await response.json();
            }} else {{
                return {{ text: await response.text() }};
            }}
        }} catch (error) {{
            return {{ error: error.message }};
        }}
    }}
}}

(async () => {{
    const client = new ApiClient({f'"{user_token}"' if user_token else "null"});
    let testParams = null;
    let testData = null;

    if ("{method}" === "GET") {{
        testParams = {{ "latitude": 11.01, "longitude": 76.96, "hourly": "temperature_2m" }};
    }} else {{
        testData = {json.dumps(body_template)};
    }}

    const result = await client.callApi(testData, null, testParams);
    console.log("FINAL RESPONSE:", JSON.stringify(result, null, 2));
}})();
"""
        filename = "generated_api_client.js"
        
    elif language.lower() == "java":
        java_payload = json.dumps(body_template).replace('"', '\\"')
        code = f"""import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.Map;
import java.util.HashMap;

public class ApiClient {{
    private final String baseUrl;
    private final String apiKey;

    public ApiClient(String apiKey) {{
        this.baseUrl = "{base_url}";
        this.apiKey = apiKey;
    }}

    public String callApi(String jsonData, String userId, Map<String, String> params) {{
        try {{
            String currentEndpoint = "{endpoint}";
            if (userId != null && !userId.isEmpty()) {{
                if (currentEndpoint.contains("{{user_id}}")) {{
                    currentEndpoint = currentEndpoint.replace("{{user_id}}", userId);
                }} else {{
                    currentEndpoint = currentEndpoint.replaceAll("/+$", "") + "/" + userId;
                }}
            }}

            StringBuilder urlBuilder = new StringBuilder(this.baseUrl).append(currentEndpoint);
            if (params != null && !params.isEmpty()) {{
                urlBuilder.append("?");
                params.forEach((k, v) -> urlBuilder.append(k).append("=").append(v).append("&"));
            }}

            HttpClient client = HttpClient.newHttpClient();
            HttpRequest.Builder requestBuilder = HttpRequest.newBuilder()
                .uri(URI.create(urlBuilder.toString()))
                .header("Content-Type", "application/json")
                .header("User-Agent", "Java-HttpClient");

            if (this.apiKey != null && !"{auth_type}".equals("None")) {{
                String authHeader = "{auth_type}".equals("Bearer") ? "Bearer " + this.apiKey : this.apiKey;
                requestBuilder.header("{header_name}", authHeader);
            }}

            if ("{method}".equals("GET")) {{
                requestBuilder.GET();
            }} else {{
                requestBuilder.method("{method}", HttpRequest.BodyPublishers.ofString(jsonData != null ? jsonData : "{{}}"));
            }}

            System.out.println("\\n--- Making {method} request to: " + urlBuilder.toString() + " ---");
            HttpResponse<String> response = client.send(requestBuilder.build(), HttpResponse.BodyHandlers.ofString());
            return response.body();

        }} catch (Exception e) {{
            return "Error: " + e.getMessage();
        }}
    }}

    public static void main(String[] args) {{
        String token = {f'"{user_token}"' if user_token else "null"};
        ApiClient client = new ApiClient(token);
        String result;
        if ("{method}".equals("GET")) {{
            Map<String, String> weatherParams = new HashMap<>();
            weatherParams.put("latitude", "11.01");
            weatherParams.put("longitude", "76.96");
            weatherParams.put("hourly", "temperature_2m");
            result = client.callApi(null, null, weatherParams);
        }} else {{
            String payload = "{java_payload}";
            result = client.callApi(payload, null, null);
        }}
        System.out.println("FINAL RESPONSE:\\n" + result);
    }}
}}
"""
        filename = "ApiClient.java"

    else:
        # --- PYTHON TEMPLATE (FIXED INDENTATION) ---
        code = f"""import requests
import json

class ApiClient:
    def __init__(self, api_key=None):
        self.base_url = "{base_url}"
        self.api_key = api_key
        self.headers = {{
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Content-Type": "application/json"
        }}
        
        if self.api_key and "{auth_type}" != "None":
            if "{auth_type}" == "API-Key":
                self.headers["x-api-key"] = self.api_key
            elif "{auth_type}" == "Bearer":
                self.headers["Authorization"] = f"Bearer {{self.api_key}}"
            else:
                self.headers["{header_name}"] = self.api_key

    def call_api(self, data=None, user_id=None, params=None):
        current_endpoint = "{endpoint}"
        if user_id:
            if "{{user_id}}" in current_endpoint:
                current_endpoint = current_endpoint.replace("{{user_id}}", str(user_id))
            else:
                current_endpoint = f"{{current_endpoint.rstrip('/')}}/{{user_id}}"
        
        url = f"{{self.base_url}}{{current_endpoint}}"
        query_params = params if params else {{}}
        print(f"\\n--- Making {method} request to: {{url}} ---")

        try:
            response = requests.request(
                "{method}", 
                url, 
                headers=self.headers, 
                json=data, 
                params=query_params,
                timeout=15
            )
            if not response.ok:
                return {{"error": f"Server Error {{response.status_code}}", "details": response.text}}
            return response.json() if 'application/json' in response.headers.get('Content-Type', '') else {{"text": response.text}}
        except Exception as e:
            return {{"error": str(e)}}

# --- EXECUTION BLOCK (OUTSIDE THE CLASS) ---
client = ApiClient(api_key={f'"{user_token}"' if user_token else "None"})

if "{method}" == "GET":
    test_params = {{ "latitude": 11.01, "longitude": 76.96, "hourly": "temperature_2m" }}
    result = client.call_api(params=test_params)
else:
    test_payload = {json.dumps(body_template)}
    if not test_payload:
        test_payload = {{"name": "Test Item", "data": {{"info": "auto-generated"}}}}
    result = client.call_api(data=test_payload)

print(json.dumps(result, indent=4))
"""
        filename = "generated_api_client.py"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(code)
    return filename