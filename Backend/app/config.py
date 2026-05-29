import os
from email.utils import parseaddr
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
    REQUEST_MAX_BODY_BYTES = int(os.getenv("REQUEST_MAX_BODY_BYTES", 1048576))  # 1MB default
    SECURITY_HEADERS_ENABLED = os.getenv("SECURITY_HEADERS_ENABLED", "True").lower() == "true"

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

    # Database optimization (Phase 10 Step 7)
    DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", 10))
    DB_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", 20))
    DB_POOL_RECYCLE_SECONDS = int(os.getenv("DB_POOL_RECYCLE_SECONDS", 3600))
    DB_POOL_TIMEOUT_SECONDS = int(os.getenv("DB_POOL_TIMEOUT_SECONDS", 30))
    DB_POOL_PRE_PING = os.getenv("DB_POOL_PRE_PING", "True").lower() == "true"

    # Email reporting (Phase 8 Step 1-2)
    EMAIL_ENABLED = os.getenv("EMAIL_ENABLED", "False").lower() == "true"
    SMTP_HOST = os.getenv("SMTP_HOST", "")
    SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
    SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "True").lower() == "true"
    SMTP_TIMEOUT_SECONDS = int(os.getenv("SMTP_TIMEOUT_SECONDS", 30))
    EMAIL_SENDER = os.getenv("EMAIL_SENDER", "")
    EMAIL_ADMIN_RECIPIENTS = [x.strip() for x in os.getenv("EMAIL_ADMIN_RECIPIENTS", "").split(",") if x.strip()]
    EMAIL_FACULTY_RECIPIENTS = [x.strip() for x in os.getenv("EMAIL_FACULTY_RECIPIENTS", "").split(",") if x.strip()]
    EMAIL_RETRY_LIMIT = int(os.getenv("EMAIL_RETRY_LIMIT", 2))
    EMAIL_RETRY_BACKOFF_SECONDS = int(os.getenv("EMAIL_RETRY_BACKOFF_SECONDS", 2))
    EMAIL_AUTOMATION_ENABLED = os.getenv("EMAIL_AUTOMATION_ENABLED", "False").lower() == "true"
    EMAIL_DAILY_RECIPIENT_GROUP = os.getenv("EMAIL_DAILY_RECIPIENT_GROUP", "admin")
    EMAIL_MONTHLY_AUTOMATION_ENABLED = os.getenv("EMAIL_MONTHLY_AUTOMATION_ENABLED", "False").lower() == "true"
    EMAIL_MONTHLY_DAY = int(os.getenv("EMAIL_MONTHLY_DAY", 1))
    EMAIL_MONTHLY_HOUR = int(os.getenv("EMAIL_MONTHLY_HOUR", 18))
    EMAIL_MONTHLY_MINUTE = int(os.getenv("EMAIL_MONTHLY_MINUTE", 0))
    EMAIL_MONTHLY_RECIPIENT_GROUP = os.getenv("EMAIL_MONTHLY_RECIPIENT_GROUP", "admin")

    # Dashboard analytics (Phase 9 Step 7-9)
    ANALYTICS_DEFAULT_TREND_DAYS = int(os.getenv("ANALYTICS_DEFAULT_TREND_DAYS", 7))
    ANALYTICS_MAX_TREND_DAYS = int(os.getenv("ANALYTICS_MAX_TREND_DAYS", 31))
    ANALYTICS_ENABLE_PERF_METRICS = os.getenv("ANALYTICS_ENABLE_PERF_METRICS", "True").lower() == "true"

    # API scalability guards (Phase 10 Step 9)
    API_MAX_PAGE_SIZE = int(os.getenv("API_MAX_PAGE_SIZE", 100))
    API_MAX_SEARCH_LENGTH = int(os.getenv("API_MAX_SEARCH_LENGTH", 100))

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
        if self.REQUEST_MAX_BODY_BYTES <= 0:
            raise ValueError("REQUEST_MAX_BODY_BYTES must be > 0")
        if self.DB_POOL_SIZE <= 0:
            raise ValueError("DB_POOL_SIZE must be > 0")
        if self.DB_MAX_OVERFLOW < 0:
            raise ValueError("DB_MAX_OVERFLOW must be >= 0")
        if self.DB_POOL_RECYCLE_SECONDS <= 0:
            raise ValueError("DB_POOL_RECYCLE_SECONDS must be > 0")
        if self.DB_POOL_TIMEOUT_SECONDS <= 0:
            raise ValueError("DB_POOL_TIMEOUT_SECONDS must be > 0")
        if self.API_MAX_PAGE_SIZE <= 0:
            raise ValueError("API_MAX_PAGE_SIZE must be > 0")
        if self.API_MAX_SEARCH_LENGTH <= 0:
            raise ValueError("API_MAX_SEARCH_LENGTH must be > 0")

    @staticmethod
    def _is_valid_email(value: str) -> bool:
        _, addr = parseaddr(value)
        return bool(addr and "@" in addr and "." in addr.split("@")[-1])

    def validate_email_settings(self) -> None:
        if not self.EMAIL_ENABLED:
            return
        if not self.SMTP_HOST:
            raise ValueError("SMTP_HOST is required when EMAIL_ENABLED=true")
        if self.SMTP_PORT <= 0 or self.SMTP_PORT > 65535:
            raise ValueError("SMTP_PORT must be between 1 and 65535")
        if not self.SMTP_USERNAME:
            raise ValueError("SMTP_USERNAME is required when EMAIL_ENABLED=true")
        if not self.SMTP_PASSWORD:
            raise ValueError("SMTP_PASSWORD is required when EMAIL_ENABLED=true")
        if not self.EMAIL_SENDER or not self._is_valid_email(self.EMAIL_SENDER):
            raise ValueError("EMAIL_SENDER must be a valid email when EMAIL_ENABLED=true")
        recipients = self.EMAIL_ADMIN_RECIPIENTS + self.EMAIL_FACULTY_RECIPIENTS
        if not recipients:
            raise ValueError("At least one recipient is required when EMAIL_ENABLED=true")
        invalid = [email for email in recipients if not self._is_valid_email(email)]
        if invalid:
            raise ValueError("Invalid recipient emails in configuration")
        if self.SMTP_TIMEOUT_SECONDS <= 0:
            raise ValueError("SMTP_TIMEOUT_SECONDS must be > 0")
        if self.EMAIL_RETRY_LIMIT < 0:
            raise ValueError("EMAIL_RETRY_LIMIT must be >= 0")
        if self.EMAIL_RETRY_BACKOFF_SECONDS < 0:
            raise ValueError("EMAIL_RETRY_BACKOFF_SECONDS must be >= 0")
        if self.EMAIL_DAILY_RECIPIENT_GROUP not in {"admin", "faculty", "all"}:
            raise ValueError("EMAIL_DAILY_RECIPIENT_GROUP must be one of: admin, faculty, all")
        if self.EMAIL_MONTHLY_RECIPIENT_GROUP not in {"admin", "faculty", "all"}:
            raise ValueError("EMAIL_MONTHLY_RECIPIENT_GROUP must be one of: admin, faculty, all")
        if not (1 <= self.EMAIL_MONTHLY_DAY <= 28):
            raise ValueError("EMAIL_MONTHLY_DAY must be between 1 and 28")
        if not (0 <= self.EMAIL_MONTHLY_HOUR <= 23):
            raise ValueError("EMAIL_MONTHLY_HOUR must be between 0 and 23")
        if not (0 <= self.EMAIL_MONTHLY_MINUTE <= 59):
            raise ValueError("EMAIL_MONTHLY_MINUTE must be between 0 and 59")
        if self.ANALYTICS_DEFAULT_TREND_DAYS < 2:
            raise ValueError("ANALYTICS_DEFAULT_TREND_DAYS must be >= 2")
        if self.ANALYTICS_MAX_TREND_DAYS < self.ANALYTICS_DEFAULT_TREND_DAYS:
            raise ValueError("ANALYTICS_MAX_TREND_DAYS must be >= ANALYTICS_DEFAULT_TREND_DAYS")

# Singleton instance
settings = Settings()
