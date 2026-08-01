import os
import io
import base64
import uuid
from PIL import Image
from werkzeug.utils import secure_filename
from config import Config

def save_upload(file_storage):
    """Writes the upload to a scratch file so the Groq vision call can read
    it. This is temporary — it gets deleted right after processing. It is
    NOT how photos are kept long-term anymore; see to_data_uri() below."""
    filename = secure_filename(file_storage.filename)
    unique_name = f"{uuid.uuid4().hex}_{filename}"
    path = os.path.join(Config.UPLOAD_FOLDER, unique_name)
    file_storage.save(path)
    return path.replace("\\", "/")

def encode_image_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def to_data_uri(path, max_dimension=900, quality=78):
    """Resizes the image down and returns it as a data: URI string. This is
    what actually gets stored in the database now, so a photo survives
    restarts/redeploys instead of living on disk."""
    img = Image.open(path)
    img = img.convert("RGB")
    img.thumbnail((max_dimension, max_dimension))
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=quality, optimize=True)
    encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/jpeg;base64,{encoded}"

def cleanup_temp(path):
    try:
        os.remove(path)
    except OSError:
        pass