
# logger.py
# Provides a consistent logger for the application, logging to both console and app.log with rotation.


# Standard library imports
import logging
import sys
import os
from logging.handlers import RotatingFileHandler


# Path for the log file at the project root
LOG_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'app.log')


# Configure the root logger for the application
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        RotatingFileHandler(LOG_FILE_PATH, maxBytes=5*1024*1024, backupCount=5, encoding='utf-8')
    ]
)

def get_logger(name):
    """
    Returns a logger instance with the specified name for consistent logging.
    Usage:
        logger = get_logger(__name__)
        logger.info("message")
    """
    return logging.getLogger(name)