import streamlit as st
import httpx
import json
import re
import tempfile
import subprocess

st.set_page_config(page_title="AI Code Assistant", layout="wide")

# Session State Init
if "generated_code" not in st.session_state:
    st.session_state.generated_code = ""
if "extracted_endpoints" not in st.session_state:
    st.session_state.extracted_endpoints = []
if "editable_endpoints" not in st.session_state:
    st.session_state.editable_endpoints = []

# Ollama Stream
def stream_code_from_ollama(prompt, model="codellama"):
    url = "http://localhost:11434/api/generate"
    headers = {"Content-Type": "application/json"}
    data = {
        "model": model,
        "prompt": prompt,
        "stream": True
    }
    with httpx.stream("POST", url, json=data, headers=headers, timeout=120) as response:
        for line in response.iter_lines():
            if line:
                try:
                    json_chunk = json.loads(line)
                    yield json_chunk.get("response", "")
                except Exception:
                    continue

# UI
st.title("🧠 AI Code Assistant + API Tester")

prompt = st.text_area("Enter your prompt", placeholder="e.g., Build a FastAPI with CRUD for users")

if st.button("Generate Code"):
    full_prompt = f"""
You are an expert Python developer.

### Instruction:
{prompt}

### Response:
Provide:
1. Python FastAPI code
2. A list of endpoints in this format:

<code>
# FastAPI code
</code>

<endpoints>
GET /users
POST /users
</endpoints>
"""
    generated = ""
    placeholder = st.empty()
    with st.spinner("Generating code..."):
        for token in stream_code_from_ollama(full_prompt):
            generated += token
            placeholder.code(generated, language="python")

    code_match = re.search(r"<code>(.*?)</code>", generated, re.DOTALL)
    endpoints_match = re.search(r"<endpoints>(.*?)</endpoints>", generated, re.DOTALL)

    if code_match:
        st.session_state.generated_code = code_match.group(1).strip()
    else:
        st.session_state.generated_code = generated.strip()

    if endpoints_match:
        extracted = endpoints_match.group(1).strip().splitlines()
        st.session_state.extracted_endpoints = extracted
        st.session_state.editable_endpoints = extracted

st.text_area("Generated Code", st.session_state.generated_code, height=300)

# Editable Endpoint Table
st.subheader("🛠️ Extracted + Editable Endpoints")
new_endpoints = []
for i, ep in enumerate(st.session_state.editable_endpoints):
    col1, col2 = st.columns([1, 3])
    with col1:
        method = st.selectbox(f"Method {i+1}", ["GET", "POST", "PUT", "DELETE"], index=["GET", "POST", "PUT", "DELETE"].index(ep.split(" ")[0]), key=f"method_{i}")
    with col2:
        route = st.text_input(f"Route {i+1}", value=ep.split(" ")[1], key=f"route_{i}")
    new_endpoints.append(f"{method} {route}")
st.session_state.editable_endpoints = new_endpoints

# Headers and Body Input
st.subheader("📦 Request Config")
headers = st.text_area("Headers (JSON)", '{"Content-Type": "application/json"}')
body = st.text_area("Body (JSON)", '{"example": "data"}')

# Run Newman Test
if st.button("Test API Collection"):
    try:
        parsed_headers = json.loads(headers)
        parsed_body = json.loads(body)
    except:
        st.error("Invalid JSON in headers or body.")
        st.stop()

    # Construct Postman collection
    items = []
    for ep in st.session_state.editable_endpoints:
        method, path = ep.split(" ", 1)
        full_url = f"http://localhost:8000{path.replace('{id}', '1')}"

        items.append({
            "name": f"{method} {path}",
            "request": {
                "method": method,
                "header": [{"key": k, "value": v} for k, v in parsed_headers.items()],
                "body": {
                    "mode": "raw",
                    "raw": json.dumps(parsed_body)
                } if method in ["POST", "PUT"] else {},
                "url": {
                    "raw": full_url
                }
            }
        })

    collection = {
        "info": {
            "name": "Generated API Collection",
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        },
        "item": items
    }

    with tempfile.NamedTemporaryFile("w+", suffix=".json", delete=False) as tmp:
        json.dump(collection, tmp)
        tmp.flush()

        with st.spinner("Running Docker container for Postman tests..."):
            try:
                result = subprocess.run([
                    "docker", "run", "--rm",
                    "-v", f"{tmp.name}:/etc/newman/collection.json",
                    "postman/newman",
                    "run", "/etc/newman/collection.json"
                ], capture_output=True, text=True, check=True)
                st.success("API tests completed successfully.")
                st.text_area("🧪 Newman Output", result.stdout, height=300)
            except subprocess.CalledProcessError as e:
                st.error("Newman test failed.")
                st.text_area("❌ Error Output", e.stderr or e.stdout, height=300)
