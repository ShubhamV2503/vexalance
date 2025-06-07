
from flask import Flask, render_template_string, request, session, redirect, url_for
import requests
import os
import spacy
from spacy_wordnet.wordnet_annotator import WordnetAnnotator

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Needed for session

# Load spaCy model and add WordNet annotator
nlp = spacy.load("en_core_web_sm")
nlp.add_pipe("wordnet", after="lemmatizer")

def generate_code(prompt, output_dir="outputs"):
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "qwen2.5-coder:7b",
        "prompt": prompt,
        "stream": False
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        result = response.json()
        code = result["response"].strip()
        # Remove triple backticks and language identifier (e.g., ```python)
        if code.startswith("```"):
            first_newline = code.find("\n")
            if first_newline != -1:
                code = code[first_newline + 1:]
            code = code.rsplit("```", 1)[0] if code.endswith("```") else code
        # Remove triple quotes as well (precautionary)
        code = code.strip("'''").strip('"""').strip()
        return code, output_dir
    except requests.RequestException as e:
        return f"Error: {e}", None

def detect_intent(prompt):
    """
    Use spaCy to detect the intent of the prompt (follow-up, conversion, or new query).
    Returns a tuple (is_follow_up, is_conversion).
    """
    doc = nlp(prompt.lower())

    # Detect follow-up intent dynamically
    is_follow_up = False
    # Seed verbs for synonym detection
    seed_follow_up_verbs = {"modify", "edit", "improve", "change", "add", "update", "enhance"}

    for token in doc:
        # Check for pronouns indicating reference to previous context
        if token.pos_ == "PRON" and token.dep_ in {"nsubj", "dobj"}:
            is_follow_up = True
            break

        # Check for verbs that indicate modification or action
        if token.pos_ == "VERB":
            synsets = token._.wordnet.synsets()
            for synset in synsets:
                for lemma in synset.lemmas():
                    if lemma.name().lower() in seed_follow_up_verbs:
                        is_follow_up = True
                        break
                if is_follow_up:
                    break
            if is_follow_up:
                break

    # Detect conversion intent
    is_conversion = False
    conversion_verbs = {"convert", "translate"}
    for token in doc:
        if token.lemma_ in conversion_verbs:
            for next_token in doc[token.i + 1:token.i + 4]:
                if next_token.text in {"to", "into"}:
                    for further_token in doc[next_token.i + 1:next_token.i + 3]:
                        if "python" in further_token.text.lower():
                            is_conversion = True
                            break
                    if is_conversion:
                        break
            if is_conversion:
                break

    return is_follow_up, is_conversion

HTML_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🧠 Code Generator</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
        }
        #chat-container {
            max-height: 70vh;
            overflow-y: auto;
            padding: 1.5rem;
            background-color: #2d2d2d;
            border-radius: 0.5rem;
            margin: 1rem;
        }
        .bot-message {
            background-color: #3f3f3f;
            color: #e5e5e5;
            border-radius: 1rem;
            padding: 1rem;
            margin-bottom: 1rem;
            max-width: 80%;
            margin-right: auto;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
        }
        #input-form {
            position: sticky;
            bottom: 0;
            background: #1e1e1e;
            padding: 1rem;
            border-top: 1px solid #444;
            box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.2);
        }
        textarea {
            background-color: #2d2d2d;
            color: #e5e5e5;
            border: 1px solid #444;
        }
        textarea::placeholder {
            color: #888;
        }
        button {
            transition: background-color 0.3s ease;
        }
    </style>
</head>
<body class="bg-gray-900 flex flex-col h-screen">
    <div class="flex-1 overflow-hidden">
        <h1 class="text-2xl font-bold text-center p-4 bg-gradient-to-r from-indigo-600 to-purple-600 text-white shadow-lg">🧠 Code Generator</h1>
        <div id="chat-container" class="flex flex-col">
            {% if conversation %}
                {% for entry in conversation %}
                    <div class="bot-message">
                        <pre>{{ entry.code }}</pre>
                    </div>
                {% endfor %}
            {% else %}
                <div class="text-center text-gray-400 mt-4">
                    Start by entering a prompt below!
                </div>
            {% endif %}
        </div>
    </div>
    <form id="input-form" method="post" class="flex gap-2">
        <textarea name="prompt" rows="2" class="flex-1 p-2 border rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-indigo-500" placeholder="Enter your prompt here..." required>{{ last_prompt|default('', true) }}</textarea>
        <button type="submit" class="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition duration-300">Send</button>
    </form>

    {% if message %}
        <p class="text-red-400 text-center mt-2">{{ message }}</p>
    {% endif %}

    <script>
        const chatContainer = document.getElementById('chat-container');
        chatContainer.scrollTop = chatContainer.scrollHeight;

        // Prevent form submission from clearing the textarea (optional, as a fallback)
        document.getElementById('input-form').addEventListener('submit', function(event) {
            const textarea = document.querySelector('textarea[name="prompt"]');
            sessionStorage.setItem('lastPrompt', textarea.value);
        });

        // Restore the prompt if it was cleared (optional, as a fallback)
        window.addEventListener('load', function() {
            const textarea = document.querySelector('textarea[name="prompt"]');
            const savedPrompt = sessionStorage.getItem('lastPrompt');
            if (savedPrompt && !textarea.value) {
                textarea.value = savedPrompt;
            }
        });
    </script>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        session["conversation"] = []
        session.modified = True
        return render_template_string(HTML_TEMPLATE, conversation=session.get("conversation", []), last_prompt="", message=None)

    message = None
    last_prompt = ""

    if request.method == "POST":
        raw_prompt = request.form.get("prompt", "").strip()
        last_prompt = raw_prompt  # Store the prompt to repopulate the textarea

        if not raw_prompt:
            message = "Please enter a prompt."
        else:
            # Detect intent using spaCy (still needed for prompt generation)
            is_follow_up, is_conversion = detect_intent(raw_prompt)

            # Default instruction for generating Python code
            extra_instruction = "Provide the complete code including the function definition and example usage to run the function. Do not include explanations or extra text, only the code."

            # Instruction for code conversion
            conversion_instruction = "Convert the provided JavaScript code to Python. Preserve the functionality and structure, replacing JavaScript-specific syntax (e.g., console.log) with Python equivalents (e.g., print). Provide the complete Python code with example usage to run the function. Do not include explanations or extra text, only the code."

            if "conversation" not in session:
                session["conversation"] = []
            conversation = session["conversation"]

            # Always maintain a single entry in the conversation
            # If the conversation is empty, we'll add one entry; otherwise, overwrite the existing one
            if is_follow_up and conversation:
                last_entry = conversation[-1]
                last_code = last_entry["code"]
                follow_up_instruction = "Preserve the existing functionality of the following code and integrate the new functionality requested below. Ensure all existing routes, logic, and example usage are retained while adding the new features. Provide the complete code including all function definitions and example usage to run the functions. Do not include explanations or extra text, only the code."
                full_prompt = f"{last_code}\n\n# Follow-up: {raw_prompt}\n\n{follow_up_instruction}"
            else:
                # Use conversion instruction if the query involves conversion
                instruction = conversion_instruction if is_conversion else extra_instruction
                full_prompt = f"{raw_prompt}\n\n{instruction}"

            # Generate the code
            code, path = generate_code(full_prompt)
            if path is None:
                message = code
            else:
                # Always overwrite the conversation to have exactly one entry
                if len(conversation) == 0:
                    conversation.append({"prompt": raw_prompt, "code": code})
                else:
                    conversation[0] = {"prompt": raw_prompt, "code": code}
                session["conversation"] = conversation

            print(f"Conversation length: {len(conversation)}")
            session.modified = True

    return render_template_string(HTML_TEMPLATE, conversation=session.get("conversation", []), last_prompt=last_prompt, message=message)

if __name__ == "__main__":
    app.run(debug=True)


