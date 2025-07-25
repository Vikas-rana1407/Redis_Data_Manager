import gradio as gr
from app.videos.runner import run_video_pipeline  # ✅ Correct function name

def render_add_data_tab():
    with gr.Column():
        with gr.Tab("Book"):
            gr.Markdown("### Upload Book CSV")
            csv_input = gr.File(file_types=[".csv"], label="Upload CSV")
            upload_book_btn = gr.Button("Process & Save Book", variant="primary")
            book_output = gr.Textbox(label="Processed Book Data (JSON)")

        with gr.Tab("Video"):
            gr.Markdown("### Upload YouTube Video")
            youtube_input = gr.Textbox(
                label="YouTube URL",
                placeholder="Enter the full YouTube video link"
            )
            upload_video_btn = gr.Button("Process & Save Video", variant="primary")

            # ✅ JSON viewer for clean structure and readability
            video_output = gr.JSON(label="Processed Video Data (Saved to Redis)")

            def handle_video_upload(youtube_url):
                if not youtube_url.strip():
                    return {"error": "❌ Please enter a YouTube video URL."}
                return run_video_pipeline(youtube_url)

            upload_video_btn.click(
                handle_video_upload,
                inputs=[youtube_input],
                outputs=[video_output]
            )
