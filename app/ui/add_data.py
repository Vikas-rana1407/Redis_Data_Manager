
# Standard library imports
import os
import shutil

# Third-party imports
import gradio as gr

# App imports
from app.videos.runner import run_video_pipeline
from app.books.processor import process_book_csv
from app.utils.logger import get_logger

# Constants
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "data", "uploaded_books")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Logger setup
logger = get_logger(__name__)

def save_uploaded_file(file_obj, dest_path):
    """Save uploaded file to destination path."""
    if hasattr(file_obj, 'file') and hasattr(file_obj.file, 'read'):
        file_obj.file.seek(0)
        with open(dest_path, "wb") as out_f:
            out_f.write(file_obj.file.read())
    elif hasattr(file_obj, 'read'):
        file_obj.seek(0)
        with open(dest_path, "wb") as out_f:
            out_f.write(file_obj.read())
    elif hasattr(file_obj, 'name') and os.path.exists(file_obj.name):
        shutil.copyfile(file_obj.name, dest_path)
    else:
        raise ValueError("Unsupported file object type for upload.")

def process_and_log_csv(path, logger):
    """Process CSV and log results."""
    try:
        books_json, summary = process_book_csv(path)
        logger.info(f"Processed book CSV: {path} | Summary: {summary}")
        return {
            "summary": summary,
            "processed_books": books_json
        }
    except Exception as e:
        logger.error(f"Error processing book CSV: {e}")
        return {"error": f"❌ Error processing CSV: {e}"}

def handle_book_upload(file_obj, upload_folder, logger):
    """
    Handles the upload and processing of a book CSV file.
    Logs the upload and processing steps.
    Refactored for lower cognitive complexity and SonarQube guidelines.
    """
    if not file_obj:
        logger.warning("No CSV file uploaded for books.")
        return {"error": "❌ Please upload a CSV file."}

    dest_path = os.path.join(upload_folder, os.path.basename(file_obj.name))
    try:
        save_uploaded_file(file_obj, dest_path)
        logger.info(f"Book CSV uploaded and saved to: {dest_path}")
    except Exception as e:
        logger.error(f"Failed to save uploaded CSV: {e}")
        return {"error": f"❌ Failed to save uploaded CSV: {e}"}

    return process_and_log_csv(dest_path, logger)

def handle_video_upload(youtube_url, logger):
    """
    Handles the upload and processing of a YouTube video URL.
    Logs the upload and processing steps.
    """
    if not youtube_url.strip():
        logger.warning("No YouTube URL provided for video upload.")
        return {"message": "❌ Please enter a YouTube video URL."}
    try:
        result = run_video_pipeline(youtube_url)
        logger.info(f"Processed YouTube video: {youtube_url}")
        return result
    except Exception as e:
        logger.error(f"Error processing YouTube video: {e}")
        return {"error": f"❌ Error processing video: {e}"}

def render_add_data_tab():
    """
    Renders the Add Data tab for uploading books (CSV) and YouTube videos.
    Includes logging for all major actions and errors.
    """
    with gr.Column():
        # Book Upload Tab
        with gr.Tab("📚Book"):
            gr.Markdown("### Upload Book CSV")
            csv_input = gr.File(file_types=[".csv"], label="Upload CSV")
            upload_book_btn = gr.Button("Process & Save Book", variant="primary")
            book_output = gr.Json(label="Processed Book Data (JSON)")

            upload_book_btn.click(
                lambda file_obj: handle_book_upload(file_obj, UPLOAD_FOLDER, logger),
                inputs=[csv_input],
                outputs=[book_output]
            )

        # Video Upload Tab
        with gr.Tab("🎥Video"):
            gr.Markdown("### Upload YouTube Video")
            youtube_input = gr.Textbox(
                label="YouTube URL",
                placeholder="Enter the full YouTube video link"
            )
            upload_video_btn = gr.Button("Process & Save Video", variant="primary")
            video_output = gr.JSON(label="Processed Video Data (Saved to Redis)")

            upload_video_btn.click(
                lambda youtube_url: handle_video_upload(youtube_url, logger),
                inputs=[youtube_input],
                outputs=[video_output]
            )
