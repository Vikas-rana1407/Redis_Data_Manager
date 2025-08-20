
# Standard library imports
import os

# Third-party imports
import gradio as gr
from dotenv import load_dotenv

# App imports
from app.ui.header import render_header
from app.ui.add_data import render_add_data_tab
from app.ui.search_data import render_search_data_tab
from app.ui.delete_data import render_delete_data_tab
from app.utils.logger import get_logger

# Logger setup
logger = get_logger(__name__)

# Load environment variables
load_dotenv()

# Ensure credentials are always str (fallback to 'admin' if not set)
VALID_USERNAME = os.getenv("APP_USERNAME") 
VALID_PASSWORD = os.getenv("APP_PASSWORD") 

def main_app():
    """
    Main Gradio app: renders header and all data tabs.
    """
    with gr.Blocks(title="Redis Data Manager", theme="default") as app:
        render_header()
        with gr.Tab("➕Add Data"):
            render_add_data_tab()
        with gr.Tab("🔍Search Data"):
            render_search_data_tab()
        with gr.Tab("🗑️Delete Data"):
            render_delete_data_tab()
    logger.info("Main Gradio app UI loaded.")
    return app

def launch(server_name: str = "0.0.0.0", server_port: int = 7860):
    """
    Launches the Gradio app with authentication.
    """
    app = main_app()
    logger.info("Launching Gradio app with authentication.")
    username = VALID_USERNAME if VALID_USERNAME else "admin"
    password = VALID_PASSWORD if VALID_PASSWORD else "admin"
    app.launch(auth=(username, password), server_name=server_name, server_port=server_port)


