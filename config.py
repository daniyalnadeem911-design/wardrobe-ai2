import os
import tempfile
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "dev-secret-key")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    TURSO_DATABASE_URL = os.getenv("TURSO_DATABASE_URL", "")
    TURSO_AUTH_TOKEN = os.getenv("TURSO_AUTH_TOKEN", "")
    UPLOAD_FOLDER = os.path.join(tempfile.gettempdir(), "wardrobe_scratch")
    MAX_CONTENT_LENGTH = 8 * 1024 * 1024  # 8 MB upload limit
    ALLOWED_IMAGE_EXT = {"png", "jpg", "jpeg", "webp"}
    ALLOWED_DOC_EXT = {"pdf"}
    PERMANENT_SESSION_LIFETIME = timedelta(days=90)

os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)