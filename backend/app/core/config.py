from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    PDF_UPLOAD_PATH = os.getenv("PDF_UPLOAD_PATH")
    JSON_FILE_PATH = os.getenv("JSON_FILE_PATH")
    LOG_DIR = os.getenv("LOG_DIR")
    MAX_PDF_SIZE = int(os.getenv("MAX_PDF_SIZE", "1048576").split("#")[0].strip())  # Default 1MB
    MAX_CHAR_LENGTH = int(os.getenv("MAX_CHAR_LENGTH", "40000").split("#")[0].strip())  # Default 40000 characters
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 8000))
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    WORKERS: int = int(os.getenv("WORKERS", 1))
    TOKEN_LIMIT_PER_MINUTE: int = int(os.getenv("TOKEN_LIMIT_PER_MINUTE", 100))
    TOKEN_LIMIT_PER_DAY: int = int(os.getenv("TOKEN_LIMIT_PER_DAY", 1000))

    # MongoDB settings
    MONGODB_HOST = os.getenv("MONGODB_HOST")
    MONGODB_DB = os.getenv("MONGODB_DB")
    MONGODB_USER = os.getenv("MONGODB_USER")
    MONGODB_PASSWORD = os.getenv("MONGODB_PASSWORD")
    MONGODB_PORT = int(os.getenv("MONGODB_PORT", 27017))

settings = Settings()