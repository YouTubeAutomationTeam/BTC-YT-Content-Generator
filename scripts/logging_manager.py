import logging
import os
from datetime import datetime
from pathlib import Path

# Directories
LOG_DIR = Path("logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Base log file
DEFAULT_LOG_FILE = LOG_DIR / "system.log"

# Formatter
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Set up a root logger with default config
logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    datefmt=DATE_FORMAT,
    handlers=[
        logging.FileHandler(DEFAULT_LOG_FILE),
        logging.StreamHandler()
    ]
)

def get_logger(name: str, log_file: str = None):
    """
    Get a custom logger. Optionally use a separate file.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if log_file:
        custom_log_path = LOG_DIR / f"{log_file}.log"
        file_handler = logging.FileHandler(custom_log_path)
        file_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))
        logger.addHandler(file_handler)

    return logger

def log_event(message, level="info", logger_name="system"):
    logger = logging.getLogger(logger_name)
    if level == "info":
        logger.info(message)
    elif level == "warning":
        logger.warning(message)
    elif level == "error":
        logger.error(message)
    elif level == "debug":
        logger.debug(message)
    else:
        logger.info(message)

# Example usage
if __name__ == "__main__":
    log_event("Logging manager initialized.")
    custom_logger = get_logger("uploader", log_file="upload_events")
    custom_logger.info("This is a test log from the uploader module.")
