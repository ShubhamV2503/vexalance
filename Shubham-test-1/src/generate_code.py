# import requests
# import json
# import os

# def generate_code(prompt, artifact_id, output_dir="../outputs"):
#     url = "http://localhost:11434/api/generate"
#     payload = {
#         "model": "codellama:7b",
#         "prompt": prompt,
#         "stream": False
#     }

#     try:
#         response = requests.post(url, json=payload)
#         response.raise_for_status()
#         result = response.json()
#         code = result["response"].strip()

#         os.makedirs(output_dir, exist_ok=True)

#         output_path = os.path.join(output_dir, "generated_code.txt")
#         with open(output_path, "w") as f:
#             f.write(code)

#         print(f"Code saved to {output_path}")
#         return code

#     except requests.RequestException as e:
#         return f"Error: {e}"

# if __name__ == "__main__":
#     extra = "Only Give code nothing else not a single explanation or text only code" 
#     prompt = "Write a code to create a simple flask app" + extra

#     artifact_id = "f7a2b3c4-d5e6-4f7a-8b9c-0d1e2f3a4b5c"
#     print(generate_code(prompt, artifact_id))







##################################################################


# import streamlit as st
# import requests
# import os

# def generate_code(prompt, output_dir="outputs"):
#     url = "http://localhost:11434/api/generate"
#     payload = {
#         "model": "codellama:7b",
#         "prompt": prompt,
#         "stream": False
#     }

#     try:
#         response = requests.post(url, json=payload)
#         response.raise_for_status()
#         result = response.json()
#         code = result["response"].strip()

#         os.makedirs(output_dir, exist_ok=True)
#         output_path = os.path.join(output_dir, "generated_code.txt")
#         with open(output_path, "w") as f:
#             f.write(code)

#         return code, output_path

#     except requests.RequestException as e:
#         return f"Error: {e}", None

# # Streamlit UI
# st.title("🧠 Code Generator using CodeLlama")

# extra = "Only Give code nothing else not a single explanation or text only code"

# prompt = st.text_area("Enter your prompt:")
# prompt = prompt + " " + extra

# if st.button("Generate Code"):
#     if prompt.strip():
#         with st.spinner("Generating code..."):
#             code, path = generate_code(prompt)
#             if path:
#                 st.success(f"Code saved to {path}")
#             st.code(code, language="python")
#     else:
#         st.warning("Please enter a prompt.")


##################################################################


from flask import Flask, render_template_string, request, session, redirect, url_for
import requests
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Needed for session

def generate_code(prompt, output_dir="outputs"):
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "codellama:7b",
        "prompt": prompt,
        "stream": False
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        result = response.json()
        code = result["response"].strip()

        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "generated_code.txt")
        with open(output_path, "w") as f:
            f.write(code)

        return code, output_path
    except requests.RequestException as e:
        return f"Error: {e}", None

HTML_TEMPLATE = """
<!doctype html>
<title>🧠 Code Generator using CodeLlama</title>
<h1>🧠 Code Generator using CodeLlama</h1>
<form method=post>
  <textarea name=prompt rows=5 cols=60 placeholder="Enter your prompt here...">{{ prompt }}</textarea><br>
  <input type=submit value="Generate Code">
</form>

{% if code %}
  <h2>Generated Code:</h2>
  <pre style="background:#f0f0f0; padding:10px;">{{ code }}</pre>
{% endif %}

{% if message %}
  <p style="color:red;">{{ message }}</p>
{% endif %}
"""

@app.route("/", methods=["GET", "POST"])
def index():
    if "last_code" not in session:
        session["last_code"] = ""

    code = None
    message = None
    prompt = ""

    if request.method == "POST":
        raw_prompt = request.form.get("prompt", "").strip()
        prompt = raw_prompt  # to refill form if needed

        if not raw_prompt:
            message = "Please enter a prompt."
        else:
            # Check for follow-up keywords
            follow_up_keywords = ["also", "change", "modify", "edit", "improve"]
            is_follow_up = any(word in raw_prompt.lower() for word in follow_up_keywords)

            extra_instruction = "Only give code, nothing else — not a single explanation or text. Only code."

            if is_follow_up and session["last_code"]:
                full_prompt = f"{session['last_code']}\n\n# Follow-up: {raw_prompt}\n\n{extra_instruction}"
            else:
                full_prompt = f"{raw_prompt}\n\n{extra_instruction}"

            code, path = generate_code(full_prompt)
            if path is None:
                message = code  # error message
            else:
                session["last_code"] = code
                prompt = ""  # clear input after successful submission

    return render_template_string(HTML_TEMPLATE, code=code, message=message, prompt=prompt)

if __name__ == "__main__":
    app.run(debug=True)


