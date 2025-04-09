from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import PyPDF2
import google.generativeai as genai
from dotenv import load_dotenv
import re

# Load environment variables from .env
load_dotenv()

# Configure Gemini API with the key from .env
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Initialize Gemini model (we're using Gemini 2.0 Flash)
model = genai.GenerativeModel("gemini-2.0-flash")

# Set up Flask app
app = Flask(__name__)
CORS(app)  # Allow frontend running on different port to access this backend

# Function to extract text from uploaded PDF
def extract_pdf_text(file):
    reader = PyPDF2.PdfReader(file)
    return "\n".join(page.extract_text() or "" for page in reader.pages)

# Main route to generate both summary and flowchart
@app.route("/generate-summary", methods=["POST"])
def generate_summary():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    if file.filename == "":
        return jsonify({"error": "Empty file"}), 400

    try:
        # Step 1: Extract text from PDF
        text = extract_pdf_text(file)

        # Step 2: Prompt Gemini to generate a summary
        summary_prompt = f"""
You are an educational AI assistant. Summarize the content below into a well-structured explanation for a video script. Include:
- A short intro
- Key points explained simply
- A short conclusion

Text:
{text}
"""
        summary = model.generate_content(summary_prompt).text.strip()

        # Step 3: Prompt Gemini to create a Mermaid.js flowchart
        flowchart_prompt = f"""
You are a diagram assistant. Based on the following content, create a Mermaid.js flowchart.

Instructions:
- Output ONLY valid Mermaid.js syntax
- Must begin with 'graph TD;'
- No extra explanation or comments
- Use short and descriptive node labels

Text:
{text}
"""
        raw_flowchart = model.generate_content(flowchart_prompt).text.strip()

        # Step 4: Extract Mermaid code from response using regex
        mermaid_match = re.search(r"(graph\s+TD;[\s\S]*)", raw_flowchart)
        flowchart = mermaid_match.group(1) if mermaid_match else "graph TD;\nA[Could not generate flowchart]"

        # Return both summary and flowchart to frontend
        return jsonify({
            "summary": summary,
            "flowchart": flowchart
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run the Flask development server
if __name__ == "__main__":
    app.run(debug=True)
