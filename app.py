import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from converter import gemini_spec_from_prompt

load_dotenv()
app = Flask(__name__)

@app.get("/")
def index():
    return render_template("index.html")

@app.post("/api/spec")
def make_spec():
    data = request.get_json(silent=True) or {}
    prompt = (data.get("prompt") or "").strip()
    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400
    spec = gemini_spec_from_prompt(prompt)
    return jsonify(spec.model_dump())

if __name__ == "__main__":
    app.run(debug=True)