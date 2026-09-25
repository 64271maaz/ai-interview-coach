import pdfplumber

def extract_resume_text(file_stream):
    """
    Uploaded PDF file se saara text nikalta hai.
    file_stream = Flask ka request.files['resume'] object
    """
    try:
        text = ""
        with pdfplumber.open(file_stream) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

        # Bohat lamba resume ho to shuru ke ~3000 characters hi kaafi hain
        return text.strip()[:3000]

    except Exception as e:
        print(f"Resume parsing error: {e}")
        return ""