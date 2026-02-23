
from PIL import Image
import pytesseract
import pdfplumber
import tempfile
import os
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_text_from_file(upload_file):
    import shutil

    text = ""

    # Detect file type based on content_type and filename
    file_ext = None
    if upload_file.content_type:
        if "pdf" in upload_file.content_type:
            file_ext = ".pdf"
        elif "image" in upload_file.content_type:
            file_ext = ".png"  # Default to png if image, will handle more below
    if not file_ext:
        _, ext = os.path.splitext(upload_file.filename)
        file_ext = ext or ""

    with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp:
        tmp_path = tmp.name
        # save the uploaded file contents to the temp file
        shutil.copyfileobj(upload_file.file, tmp)
    
    try:
        if file_ext.lower() == ".pdf" or upload_file.content_type == "application/pdf":
            # PDF: Use pdfplumber
            with pdfplumber.open(tmp_path) as pdf:
                pages_text = []
                for page in pdf.pages:
                    pages_text.append(page.extract_text() or "")  # avoid None
                text = "\n".join(pages_text)
        elif file_ext.lower() in [".png", ".jpg", ".jpeg", ".bmp", ".tiff"] or (upload_file.content_type and "image" in upload_file.content_type):
            # Image: Use PIL and pytesseract
            with Image.open(tmp_path) as img:
                text = pytesseract.image_to_string(img)
        else:
            # Unknown type
            text = ""
    finally:
        try:
            os.remove(tmp_path)
        except Exception:
            pass

    return text