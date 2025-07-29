# app/ui/ui.py
import os
import gradio as gr
from dotenv import load_dotenv
from app.ui.header import render_header
from app.ui.add_data import render_add_data_tab
from app.ui.search_data import render_search_data_tab
from app.ui.delete_data import render_delete_data_tab


# Load environment variables
load_dotenv()
VALID_USERNAME = os.getenv("APP_USERNAME")
VALID_PASSWORD = os.getenv("APP_PASSWORD")


def main_app():
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
    app = main_app()
    app.launch(auth=(VALID_USERNAME, VALID_PASSWORD))

