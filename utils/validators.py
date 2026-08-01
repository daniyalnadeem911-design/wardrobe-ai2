from config import Config

def allowed_image(filename):
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return ext in Config.ALLOWED_IMAGE_EXT

def allowed_pdf(filename):
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return ext in Config.ALLOWED_DOC_EXT

def friendly_error(kind):
    messages = {
        "invalid_image": "That image couldn't be read. Please upload a JPG, PNG or WEBP file.",
        "invalid_pdf": "That file isn't a valid PDF. Please upload a .pdf file.",
        "missing_api_key": "AI features need a Groq API key. Add one in Settings.",
        "internet_error": "Couldn't reach the AI service. Check your internet connection and try again.",
        "detection_failed": "AI couldn't understand that item. Try a clearer photo.",
        "too_large": "File is too large. Max upload size is 8MB.",
    }
    return messages.get(kind, "Something went wrong. Please try again.")