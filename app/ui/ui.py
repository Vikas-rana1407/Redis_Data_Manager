from dotenv import load_dotenv
import gradio as gr
import os

from app.ui.header import render_header
from app.ui.add_data import render_add_data_tab
from app.ui.search_data import render_search_data_tab
from app.ui.delete_data import render_delete_data_tab

# Load environment variables
load_dotenv()
VALID_USERNAME = os.getenv("APP_USERNAME", "admin")
VALID_PASSWORD = os.getenv("APP_PASSWORD", "adminadmin")

def main_app():
    with gr.Blocks() as demo:
        render_header()
        with gr.Tab("➕Add Data"):
            render_add_data_tab()
        with gr.Tab("🔍Search Data"):
            render_search_data_tab()
        with gr.Tab("🗑️Delete Data"):
            render_delete_data_tab()
    return demo

def launch():
    app = main_app()
    app.launch(auth=(VALID_USERNAME, VALID_PASSWORD), pwa=True)
