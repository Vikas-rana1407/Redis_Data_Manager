import gradio as gr

def render_add_data_tab():
    with gr.Column():
        with gr.Tab("Book"):
            gr.Markdown("### Upload Book CSV")
            csv_input = gr.File(file_types=[".csv"], label="Upload CSV")
            upload_book_btn = gr.Button("Process & Save Book", variant="primary")
            book_output = gr.Textbox(label="Processed Book Data added to Redis (JSON)",interactive=False,lines=5)

        with gr.Tab("Video"):
            gr.Markdown("### Upload YouTube Video")
            youtube_input = gr.Textbox(label="YouTube URL")
            upload_video_btn = gr.Button("Process & Save Video", variant="primary")
            video_output = gr.Textbox(
                label="Processed Video Data added to Redis (JSON)",
                lines=10,
                interactive=False,  # ✅ Makes it read-only
                show_copy_button=True  # ✅ Optional: adds a copy button in UI
            )
