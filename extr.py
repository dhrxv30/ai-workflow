import fitz  # PyMuPDF
import re

# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    full_text = ""

    for page in doc:
        text = page.get_text()
        full_text += text + "\n"

    doc.close()
    return full_text

# Function to clean the extracted text
def clean_text(text):
    # Remove multiple newlines and extra spaces
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r'\s{2,}', ' ', text)

    # Remove page numbers like "Page 1"
    text = re.sub(r'Page \d+', '', text)

    # Remove bullet points and special symbols
    text = re.sub(r'[•–-]', '', text)

    # Strip whitespace from start and end
    return text.strip()

# Main code execution
pdf_path = r"C:\Users\dhruv\OneDrive\Desktop\code\example.pdf"  # <— Your PDF path here
raw_text = extract_text_from_pdf(pdf_path)
cleaned_text = clean_text(raw_text)

# Print the cleaned content
print(cleaned_text)
