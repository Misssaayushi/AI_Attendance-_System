import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    # Base Directory
    BASE_DIR = Path(__file__).resolve().parent.parent

    # Database settings
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "3306")
    DB_NAME = os.getenv("DB_NAME", "ai_attendance_db")
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")

    # Server settings  
    SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
    SERVER_PORT = int(os.getenv("SERVER_PORT", 8000))
    DEBUG_MODE = os.getenv("DEBUG_MODE", "True").lower() == "true"

    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")

    # API settings
    API_PREFIX = os.getenv("API_PREFIX", "/api/v1")

    # Export paths
    EXPORT_DIR = os.getenv("EXPORT_DIR", os.path.join(BASE_DIR, "exports"))

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")
    LOG_FILE = os.getenv("LOG_FILE", os.path.join(BASE_DIR, "logs", "app.log"))

    @property
    def DATABASE_URL(self) -> str:
        """Computes the SQLAlchemy Database URL."""
        return f"mysql+mysqlconnector://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

# Singleton instance
settings = Settings()
