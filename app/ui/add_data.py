import os
import gradio as gr
from app.videos.runner import run_video_pipeline
from app.books.processor import process_book_csv
import shutil

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "data", "uploaded_books")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def render_add_data_tab():
    with gr.Column():

        # ----------------------------- BOOK UPLOAD ----------------------------- #
        with gr.Tab("📚Book"):
            gr.Markdown("### Upload Book CSV")
            csv_input = gr.File(file_types=[".csv"], label="Upload CSV")
            upload_book_btn = gr.Button("Process & Save Book", variant="primary")
            book_output = gr.Json(label="Processed Book Data (JSON)")

            def handle_book_upload(file_obj):
                if not file_obj:
                    return {"error": "❌ Please upload a CSV file."}

                src_path = file_obj.name
                dest_path = os.path.join(UPLOAD_FOLDER, os.path.basename(src_path))

                # Avoid copying if source and destination are same
                if os.path.abspath(src_path) != os.path.abspath(dest_path):
                    shutil.copyfile(src_path, dest_path)

                books_json, summary = process_book_csv(dest_path)
                return {
                    "summary": summary,
                    "processed_books": books_json
                }

            upload_book_btn.click(
                handle_book_upload,
                inputs=[csv_input],
                outputs=[book_output]
            )

        # ----------------------------- VIDEO UPLOAD ----------------------------- #
        with gr.Tab("🎥Video"):
            gr.Markdown("### Upload YouTube Video")
            youtube_input = gr.Textbox(
                label="YouTube URL",
                placeholder="Enter the full YouTube video link"
            )
            upload_video_btn = gr.Button("Process & Save Video", variant="primary")

            video_output = gr.JSON(label="Processed Video Data (Saved to Redis)")

            def handle_video_upload(youtube_url):
                if not youtube_url.strip():
                    return {"message": "❌ Please enter a YouTube video URL."}
                return run_video_pipeline(youtube_url)

            upload_video_btn.click(
                handle_video_upload,
                inputs=[youtube_input],
                outputs=[video_output]
            )
