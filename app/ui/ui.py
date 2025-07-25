
import gradio as gr
from app.ui.header import render_header
from app.ui.add_data import add_data_book_ui, add_data_video_ui
from app.ui.search_data import search_data_book_ui, search_data_video_ui
from app.ui.delete_data import delete_data_book_ui, delete_data_video_ui
from app.ui.auth import setup_auth


def main_app():
    with gr.Blocks() as app:
        render_header()
        with gr.Tab("Add Data"):
            with gr.Tabs():
                book_file, book_upload_btn, book_status = add_data_book_ui()
                video_url, video_add_btn, video_status = add_data_video_ui()
        with gr.Tab("Search Data"):
            with gr.Tabs():
                _, _, _, _ = search_data_book_ui()
                _, _, _, _ = search_data_video_ui()
        with gr.Tab("Delete Data"):
            with gr.Tabs():
                _, _, _ = delete_data_book_ui()
                _, _, _ = delete_data_video_ui()
        # Add Data handlers
        def handle_book_upload(file):
            if not file:
                return "No file uploaded."
            return "Book upload logic not implemented."
        book_upload_btn.click(handle_book_upload, [book_file], [book_status])

        def handle_video_add(url):
            if not url:
                return "No URL provided."
            return f"Processed video: {url}"
        video_add_btn.click(handle_video_add, [video_url], [video_status])
    return app

def launch():
    app = main_app()
    auth_ui = setup_auth(app)
    auth_ui.launch(share=False)

# --- UI Logic ---