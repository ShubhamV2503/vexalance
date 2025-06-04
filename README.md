# vexalance# 🤖 AI Coding Assistant with API Testing (Streamlit + Ollama + Postman)

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

---

## 🚀 Getting Started

### 1. Install Dependencies

```bash
pip install streamlit httpx