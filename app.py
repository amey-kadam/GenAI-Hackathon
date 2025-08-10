import os
from flask import Flask, render_template, request, jsonify, send_file
from dotenv import load_dotenv
from converter import gemini_spec_from_prompt
from website_generator import WebsiteGenerator

load_dotenv()
app = Flask(__name__)

@app.get("/")
def index():
    return render_template("index.html")

@app.post("/api/spec")
def make_spec():
    """Legacy endpoint for getting spec JSON"""
    data = request.get_json(silent=True) or {}
    prompt = (data.get("prompt") or "").strip()
    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400
    spec = gemini_spec_from_prompt(prompt)
    return jsonify(spec.model_dump())

@app.post("/api/generate")
def generate_website():
    """New endpoint that generates and returns the complete website as a ZIP file"""
    try:
        # Get the prompt from request
        data = request.get_json(silent=True) or {}
        prompt = (data.get("prompt") or "").strip()
        if not prompt:
            return jsonify({"error": "Prompt is required"}), 400
        
        # Check for API key
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return jsonify({"error": "GEMINI_API_KEY is not configured"}), 500
        
        # Generate the spec from prompt
        print(f"Generating spec for prompt: {prompt[:100]}...")
        spec = gemini_spec_from_prompt(prompt)
        print(f"Spec generated successfully for project: {spec.project['name']}")
        
        # Generate the complete website
        print("Starting website generation...")
        generator = WebsiteGenerator(api_key)
        zip_path = generator.generate_website(spec)
        print(f"Website generated successfully at: {zip_path}")
        
        # Send the ZIP file
        return send_file(
            zip_path,
            as_attachment=True,
            download_name=f"{spec.project['name'].replace(' ', '-').lower()}.zip",
            mimetype='application/zip'
        )
        
    except UnicodeEncodeError as e:
        print(f"Unicode encoding error: {str(e)}")
        return jsonify({"error": "Text encoding issue. Please try a simpler description."}), 500
    except Exception as e:
        print(f"Error generating website: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Generation failed: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=False)
