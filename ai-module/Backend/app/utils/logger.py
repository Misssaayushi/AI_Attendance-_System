import logging
import sys
from logging.handlers import RotatingFileHandler
from app.config import settings
import os

# Create logs directory if it doesn't exist
os.makedirs(os.path.dirname(settings.LOG_FILE), exist_ok=True)

def setup_logger():
    """Configures a logger that outputs to both console and a rotating file."""
    
    logger = logging.getLogger("ai_attendance")
    logger.setLevel(settings.LOG_LEVEL)

    # Formatter for log messages
    # Format: [Timestamp] [Level] [Module] - Message
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s [%(name)s] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Console Handler (Outputs to terminal)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File Handler (Outputs to logs/app.log)
    # RotatingFileHandler: Keeps file size manageable (5MB max per file, 5 backups)
    file_handler = RotatingFileHandler(
        settings.LOG_FILE,
        maxBytes=5 * 1024 * 1024, # 5MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

# Singleton logger instance
logger = setup_logger()
