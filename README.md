# vexalance# 🤖 AI Coding Assistant with API Testing (Streamlit + Ollama + Postman 

This project is an **AI-powered coding assistant** built using **Streamlit**, **Ollama**, and **Postman (Newman)** to help developers generate backend APIs, edit them, and test them — all in one unified interface.

---

## 🔥 Features

### 🧠 AI Code Assistant
- Powered by [Ollama](https://ollama.com/) and local models like `codellama`.
- Streamlines natural language prompts into production-ready FastAPI code.
- Extracts and lists all API endpoints from the generated code.

### ✍️ Editable Endpoints
- View and edit auto-extracted API endpoints (e.g., `GET /users`, `POST /users/{id}`).
- Override HTTP methods and modify routes directly within the UI.

### 📦 Request Configuration
- Input custom headers and body as JSON.
- Flexible enough for any API interaction.

### 🚀 One-Click API Testing
- Converts extracted endpoints into a Postman Collection.
- Uses Docker to run **Newman** tests on your local FastAPI app.
- View the full test output (success/failure and response) inline.

---

## 🧱 Tech Stack

| Tool        | Role                                  |
|-------------|---------------------------------------|
| Streamlit   | Interactive frontend                  |
| Ollama      | Local LLM serving via REST API        |
| codellama   | Code generation model                 |
| Postman     | API structure standard                |
| Newman      | API testing CLI (Dockerized)          |
| Docker      | Container runtime for Newman          |
| Python      | Backend logic + Streamlit integration |


⸻


## ⚙️ Setup Commands

### 🔧 1. Install Required Python Packages

```bash
pip install streamlit httpx


⸻

🚀 2. Start the Ollama Model Server

ollama run codellama

⚠️ Keep this running in a separate terminal.
This starts the local API server at http://localhost:11434.

⸻

🐳 3. Pull the Postman Newman Docker Image

docker pull postman/newman

Used for API testing via collection.json

⸻

💻 4. Run the FastAPI App (Optional - If Code Uses FastAPI)

uvicorn main:app --reload

Replace main with the filename containing your generated code (e.g., main.py).

⸻

🌐 5. Run the Streamlit App

streamlit run app.py

This launches the full AI assistant and API testing interface in your browser.

⸻

🧪 Usage Flow
	1.	Enter a natural language prompt like:

Create a FastAPI with CRUD operations for products.


	2.	The AI will:
	•	Generate real-time FastAPI code.
	•	Extract endpoints like GET /products, POST /products, etc.
	3.	You can:
	•	Edit any endpoint inline.
	•	Enter headers & request body as JSON.
	•	Click Test API Collection.
	4.	Newman (in Docker) will:
	•	Test the endpoints live.
	•	Show success/fail status and logs right inside the app.

⸻
