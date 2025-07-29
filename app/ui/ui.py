# app/ui/ui.py
import os
import gradio as gr
from dotenv import load_dotenv
from app.ui.header import render_header
from app.ui.add_data import render_add_data_tab
from app.ui.search_data import render_search_data_tab
from app.ui.delete_data import render_delete_data_tab
# app/ui/ui.py

"""
Main Gradio UI entry point for Redis Data Manager.
Handles tab layout and authentication.
All actions are logged to app.log.
"""

import logging


# Load environment variables
load_dotenv()
VALID_USERNAME = os.getenv("APP_USERNAME")
VALID_PASSWORD = os.getenv("APP_PASSWORD")


# Set up logger
from app.utils.logger import get_logger
logger = get_logger(__name__)

def main_app():
    with gr.Blocks(title="Redis Data Manager", theme="default") as app:
VALID_USERNAME = os.getenv("APP_USERNAME")
VALID_PASSWORD = os.getenv("APP_PASSWORD")
            render_add_data_tab()

def main_app():
    """
    Build the main Gradio Blocks app with all tabs and header.
    """
    logger.info("Launching main Gradio UI.")
    with gr.Blocks(title="Redis Data Manager", theme="default") as app:
        render_header()
        with gr.Tab("➕Add Data"):
            render_add_data_tab()
        with gr.Tab("🔍Search Data"):
            render_search_data_tab()
        with gr.Tab("🗑️Delete Data"):
            render_delete_data_tab()
    return app


# app/ui/ui.py

"""
Main Gradio UI entry point for Redis Data Manager.
Handles tab layout and authentication.
All actions are logged to app.log.
"""

import os
import gradio as gr
from dotenv import load_dotenv
from app.ui.header import render_header
from app.ui.add_data import render_add_data_tab
from app.ui.search_data import render_search_data_tab
from app.ui.delete_data import render_delete_data_tab

# Set up logger
from app.utils.logger import get_logger
logger = get_logger(__name__)

# Load environment variables
load_dotenv()
VALID_USERNAME = str(os.getenv("APP_USERNAME") or "admin")
VALID_PASSWORD = str(os.getenv("APP_PASSWORD") or "adminadmin")

def main_app():
    """
    Build the main Gradio Blocks app with all tabs and header.
    """
    logger.info("Launching main Gradio UI.")
    with gr.Blocks(title="Redis Data Manager", theme="default") as app:
        render_header()
        with gr.Tab("➕Add Data"):
            render_add_data_tab()
        with gr.Tab("🔍Search Data"):
            render_search_data_tab()
        with gr.Tab("🗑️Delete Data"):
            render_delete_data_tab()
    return app

def launch():
    """
    Launch the Gradio app with authentication.
    """
    logger.info("App launch requested.")
    app = main_app()
    app.launch(auth=(VALID_USERNAME, VALID_PASSWORD))

