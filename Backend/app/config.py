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
    CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")

    # Server settings  
    SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
    SERVER_PORT = int(os.getenv("SERVER_PORT", 8000))
    DEBUG_MODE = os.getenv("DEBUG_MODE", "True").lower() == "true"

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 # Token valid for 1 hour

    # API settings
    API_PREFIX = os.getenv("API_PREFIX", "/api/v1")

    # Export paths
    EXPORT_DIR = os.getenv("EXPORT_DIR", os.path.join(BASE_DIR, "exports"))

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")
    LOG_FILE = os.getenv("LOG_FILE", os.path.join(BASE_DIR, "logs", "app.log"))

    # Scheduler (Phase 7 Step 1-2)
    SCHEDULER_ENABLED = os.getenv("SCHEDULER_ENABLED", "True").lower() == "true"
    SCHEDULER_TIMEZONE = os.getenv("SCHEDULER_TIMEZONE", "Asia/Kolkata")
    AUTO_ABSENT_HOUR = int(os.getenv("AUTO_ABSENT_HOUR", 17))
    AUTO_ABSENT_MINUTE = int(os.getenv("AUTO_ABSENT_MINUTE", 0))
    AUTO_ABSENT_RETRY_LIMIT = int(os.getenv("AUTO_ABSENT_RETRY_LIMIT", 2))
    AUTO_ABSENT_BATCH_SIZE = int(os.getenv("AUTO_ABSENT_BATCH_SIZE", 1000))
    SCHEDULER_COALESCE = os.getenv("SCHEDULER_COALESCE", "True").lower() == "true"
    SCHEDULER_MAX_INSTANCES = int(os.getenv("SCHEDULER_MAX_INSTANCES", 1))

    @property
    def DATABASE_URL(self) -> str:
        """Computes the SQLAlchemy Database URL."""
        return f"mysql+mysqlconnector://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    def validate_scheduler_settings(self) -> None:
        if not (0 <= self.AUTO_ABSENT_HOUR <= 23):
            raise ValueError("AUTO_ABSENT_HOUR must be between 0 and 23")
        if not (0 <= self.AUTO_ABSENT_MINUTE <= 59):
            raise ValueError("AUTO_ABSENT_MINUTE must be between 0 and 59")
        if self.AUTO_ABSENT_RETRY_LIMIT < 0:
            raise ValueError("AUTO_ABSENT_RETRY_LIMIT must be >= 0")
        if self.AUTO_ABSENT_BATCH_SIZE <= 0:
            raise ValueError("AUTO_ABSENT_BATCH_SIZE must be > 0")
        if self.SCHEDULER_MAX_INSTANCES <= 0:
            raise ValueError("SCHEDULER_MAX_INSTANCES must be > 0")

# Singleton instance
settings = Settings()
