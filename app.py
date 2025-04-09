from flask import Flask, request, jsonify
import os
import PyPDF2
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

# Configure Gemini
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.0-flash")  # Or try "gemini-1.5-pro-latest" if available

app = Flask(__name__)

# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() or ""
    return text

# Function to chunk text into pieces within token/input limits
def chunk_text(text, chunk_size=5000):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

# Generate detailed educational explanation from text
def generate_detailed_summary(text):
    prompt_template = """
You are an AI educational assistant. Read the following content and create a detailed educational script suitable for a video. Follow this structure:
1. Introduction
2. Key Concepts
3. Detailed Explanation
4. Real-life Examples
5. Conclusion

Use clear and student-friendly language.

Content:
{}
"""
    chunks = chunk_text(text)
    full_script = ""
    for i, chunk in enumerate(chunks):
        prompt = prompt_template.format(chunk)
        response = model.generate_content(prompt)
        full_script += f"\n--- Section {i+1} ---\n{response.text.strip()}\n"
    return full_script.strip()

@app.route("/generate-summary", methods=["POST"])
def generate_summary():
    if "file" not in request.files:
        return jsonify({"error": "No file part in request"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    try:
        extracted_text = extract_text_from_pdf(file)
        if not extracted_text.strip():
            return jsonify({"error": "No text extracted from PDF"}), 400

        summary = generate_detailed_summary(extracted_text)
        return jsonify({"summary": summary})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
