import fitz  # PyMuPDF
import os
import uuid
from config import Config

def extract_pdf_text(file_storage):
    from PyPDF2 import PdfReader
    reader = PdfReader(file_storage)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
        text += "\n"
    return text

def extract_pdf_page_images(file_storage):
    """Fallback for image-only PDFs: render each page as a JPEG and save it."""
    file_storage.seek(0)
    pdf_bytes = file_storage.read()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    saved_paths = []
    for page in doc:
        pix = page.get_pixmap(dpi=150)
        filename = f"{uuid.uuid4().hex}_pdf_page.jpg"
        path = os.path.join(Config.UPLOAD_FOLDER, filename)
        pix.save(path)
        saved_paths.append(path)
    doc.close()
    return saved_paths