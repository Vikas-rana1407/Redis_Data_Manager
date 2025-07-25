"""
logger.py

This module is responsible for configuring and providing logger instances
for the application. It sets up the logging format, level, and handlers,
including the option to log to a file with rotation.

Usage:
    from logger import get_logger

    logger = get_logger(__name__)
    logger.info("This is an info message")
    logger.error("This is an error message")
"""

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
    Returns a logger instance with the specified name.
    Use this for consistent logging throughout the app.

    Example usage:
        logger = get_logger(__name__)
        logger.info("This is an info message")
        logger.error("This is an error message")
    """
    return logging.getLogger(name)