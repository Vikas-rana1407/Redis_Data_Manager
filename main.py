
# main.py
from app.utils.data_cleanup import start_cleanup_thread
# Entry point for the Redis Data Manager application.

# Standard library imports
import os

# Third-party imports
from dotenv import load_dotenv
import gradio as gr

# App imports
from app.ui.ui import launch
from app.utils.logger import get_logger

# Logger setup
logger = get_logger(__name__)



def main():
    """
    Entry point for the Redis Data Manager application.
    Loads environment variables and launches the Gradio UI.
    """
    load_dotenv()
    logger.info("Environment variables loaded")
    logger.info("Server will run on: http://127.0.0.1:7860")
    logger.info(f"Admin username: {os.getenv('ADMIN_USERNAME', 'admin')}")
    logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    # Start background cleanup thread
    start_cleanup_thread()
    # Launch the Gradio app
    launch()

if __name__ == "__main__":
    main()