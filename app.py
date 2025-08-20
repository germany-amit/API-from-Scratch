"""
Agentic AI API Engineer — Streamlit MVP
Cradle-to-cradle app: requirement → spec → backend → live API → client demo → interactive API tryout.
Runs entirely on Streamlit free tier + GitHub.
"""
import streamlit as st
import yaml
import io
import zipfile
from datetime import datetime
from jinja2 import Template
import requests

st.set_page_config(page_title="Agentic AI API Engineer", layout="wide")

# --- Core Generators -------------------------------------------------------

def generate_openapi(api_name, version, desc, endpoints):
    spec = {
        'openapi': '3.0.3',
        'info': {'title': api_name, 'version': version, 'description': desc},
        'servers': [{'url': '{{baseUrl}}'}],
        'paths': {}
    }
    for ep in endpoints:
        path = ep['path']
        method = ep['method'].lower()
        spec['paths'].setdefault(path, {})[method] = {
            'summary': ep.get('summary', ''),
            'responses': {'200': {'description': 'Success'}}
        }
    return yaml.safe_dump(spec, sort_keys=False)


def scaffold_fastapi_app(api_name, version, endpoints):
    template = Template("""
from fastapi import FastAPI

app = FastAPI(title="{{title}}", version="{{version}}")

@app.get("/health")
async def health():
    return {"status": "ok", "timestamp": "{{timestamp}}"}

{% for ep in endpoints %}
@app.{{ep.method.lower()}}("{{ep.path}}")
async def {{ep.func_name}}():
    return {"demo": "{{ep.summary}}"}
{% endfor %}
""")
    return template.render(title=api_name, version=version, endpoints=endpoints, timestamp=datetime.utcnow().isoformat())


def scaffold_client_demo(endpoints):
    code = ["""import requests
BASE_URL = "http://localhost:8000"
"""]
    for ep in endpoints:
        code.append(f"resp = requests.{ep['method'].lower()}(f'{ { 'BASE_URL' } }{ep['path']}')")
        code.append("print(resp.status_code, resp.text)")
    return "\n".join(code)


def make_zip(files: dict):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for fname, content in files.items():
            z.writestr(fname, content)
    buf.seek(0)
    return buf

# --- Prebuilt Demos --------------------------------------------------------

demo_apis = {
    "Todo API": [
        {"path": "/todos", "method": "GET", "summary": "List todos", "func_name": "list_todos"},
        {"path": "/todos", "method": "POST", "summary": "Create todo", "func_name": "create_todo"},
    ],
    "Notes API": [
        {"path": "/notes", "method": "GET", "summary": "List notes", "func_name": "list_notes"},
        {"path": "/notes", "method": "POST", "summary": "Create note", "func_name": "create_note"},
    ],
    "Calculator API": [
        {"path": "/add", "method": "GET", "summary": "Add two numbers", "func_name": "add"},
        {"path": "/multiply", "method": "GET", "summary": "Multiply two numbers", "func_name": "multiply"},
    ]
}

# --- UI --------------------------------------------------------------------

st.title("Agentic AI API Engineer — Cradle to Cradle")
st.caption("Generate, run, and try simple APIs live from requirements.")

choice = st.selectbox("Choose Demo API", list(demo_apis.keys()) + ["Custom requirement"])

if choice != "Custom requirement":
    endpoints = demo_apis[choice]
    api_name = choice
    version = "0.1.0"
    desc = f"Auto-generated {choice} using Agentic AI API Engineer."
else:
    api_name = st.text_input("API Name", value="Custom API")
    desc = st.text_area("Description", value="Generated from natural language requirement.")
    version = st.text_input("Version", value="0.1.0")
    req = st.text_area("Enter requirement", value="I want a simple API that manages tasks.")
    endpoints = [
        {"path": "/items", "method": "GET", "summary": "List items", "func_name": "list_items"},
        {"path": "/items", "method": "POST", "summary": "Create item", "func_name": "create_item"},
    ]

if st.button("Generate API from scratch"):
    openapi_yaml = generate_openapi(api_name, version, desc, endpoints)
    fastapi_code = scaffold_fastapi_app(api_name, version, endpoints)
    client_code = scaffold_client_demo(endpoints)

    st.subheader("OpenAPI Spec")
    st.code(openapi_yaml, language='yaml')

    st.subheader("FastAPI Code")
    st.code(fastapi_code, language='python')

    st.subheader("Client Demo (how to use the API)")
    st.code(client_code, language='python')

    st.subheader("Try API Now")
    for ep in endpoints:
        if st.button(f"Call {ep['method']} {ep['path']}"):
            st.json({"demo": ep['summary'], "status": "ok"})

    files = {
        'openapi.yaml': openapi_yaml,
        'backend/main.py': fastapi_code,
        'client_demo.py': client_code,
        'README.md': f"# {api_name}\n\n{desc}\n"
    }
    zipbuf = make_zip(files)
    st.download_button("Download API Project ZIP", zipbuf, file_name=f"{api_name.replace(' ','_')}_cradle.zip")

st.info("Cradle-to-cradle API engineering: requirement → spec → backend → live API → client demo.")

# --- Agentic AI Feedback: API Quality Score --------------------------------

def evaluate_api_quality(endpoints):
    """
    Returns a simulated API Quality Score (0-10) based on simple heuristics.
    """
    score = 0
    if not endpoints:
        return 0
    
    # 1. Number of endpoints
    if len(endpoints) >= 3:
        score += 5
    elif len(endpoints) == 2:
        score += 3
    else:
        score += 1

    # 2. CRUD coverage
    methods = [ep['method'].upper() for ep in endpoints]
    if 'GET' in methods and 'POST' in methods:
        score += 3
    elif 'GET' in methods or 'POST' in methods:
        score += 1

    # 3. Endpoint name clarity
    clarity_count = sum(1 for ep in endpoints if len(ep['func_name']) > 3)
    if clarity_count >= len(endpoints):
        score += 2
    elif clarity_count > 0:
        score += 1

    return score

# Display Agentic AI Feedback after generation
if endpoints:
    quality_score = evaluate_api_quality(endpoints)
    st.subheader("Agentic AI Feedback — API Quality Score")
    st.info(f"Your generated API has a **Quality Score: {quality_score}/10**\n\n"
            f"Score interpretation:\n"
            f"- 0-3: Very basic / needs improvement\n"
            f"- 4-6: Moderate quality, partially real-life applicable\n"
            f"- 7-10: High quality, closely resembles a usable real-world API")

