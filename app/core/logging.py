import logging
import sys
from logging.handlers import RotatingFileHandler
from app.core.config import settings

def setup_logging():
    # Create logger
    logger = logging.getLogger("smart_glasses")
    logger.setLevel(settings.LOG_LEVEL)

    # Create formatters
    formatter = logging.Formatter(settings.LOG_FORMAT)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler
    file_handler = RotatingFileHandler(
        "logs/smart_glasses.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

# Create logs directory if it doesn't exist
import os
os.makedirs("logs", exist_ok=True)

# Initialize logger
logger = setup_logging() 