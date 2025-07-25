import gradio as gr

def render_add_data_tab():
    with gr.Column():
        with gr.Tab("Book"):
            gr.Markdown("### Upload Book CSV")
            csv_input = gr.File(file_types=[".csv"], label="Upload CSV")
            upload_book_btn = gr.Button("Process & Save Book", variant="primary")
            book_output = gr.Textbox(label="Upload Status")

        with gr.Tab("Video"):
            gr.Markdown("### Upload YouTube Video")
            youtube_input = gr.Textbox(label="YouTube URL")
            upload_video_btn = gr.Button("Process & Save Video", variant="primary")
            video_output = gr.Textbox(label="Upload Status")
